"""Operator-only, repeatable embedding preparation; never reads evaluation files."""

import asyncio
import hashlib
import json
import time

import httpx
from neo4j import AsyncGraphDatabase, Query

from app.agent.ollama import DIMENSIONS, EMBED_DIGEST, EMBED_MODEL, EMBED_POLICY, INDEX, Ollama
from app.config import Settings


async def prepare(driver, model):
    """Embed missing/stale chunks in batches; fail on incompatible existing index."""
    start = time.perf_counter()
    async with driver.session() as session:
        result = await session.run(Query(
            "SHOW VECTOR INDEXES YIELD name,options,labelsOrTypes,properties WHERE name=$name "
            "RETURN options,labelsOrTypes,properties", timeout=5), name=INDEX)
        index = await result.single()
        if index:
            options = index["options"]
            if (index["labelsOrTypes"] != ["Chunk"] or index["properties"] != ["embedding"]
                    or options["indexConfig"].get("vector.dimensions") != DIMENSIONS
                    or str(options["indexConfig"].get("vector.similarity_function")).lower() != "cosine"):
                raise ValueError("Existing vector index incompatible; explicit migration required")
        result = await session.run(Query("""
MATCH (c:Chunk)-[:PART_OF]->(p:Paper)
WHERE c.paper_id=p.id AND c.pdf_sha256=p.pdf_sha256
RETURN c.id AS id, c.text AS text, c.text_sha256 AS hash, c.embedding_model AS model,
c.embedding_digest AS digest, c.embedding_dimensions AS dimensions,
c.embedding_text_sha256 AS embedded_hash, c.embedding_policy AS policy,
size(c.embedding) AS vector_size ORDER BY id
""", timeout=10))
        rows = [dict(row) async for row in result]
        if any(hashlib.sha256(r["text"].encode()).hexdigest() != r["hash"] for r in rows):
            raise ValueError("Stored chunk text hash mismatch")
        pending = [r for r in rows if (r["model"], r["digest"], r["dimensions"], r["embedded_hash"],
                   r["policy"], r["vector_size"]) !=
                   (EMBED_MODEL, EMBED_DIGEST, DIMENSIONS, r["hash"], EMBED_POLICY, DIMENSIONS)]
        await model.identity()
        written = 0
        for offset in range(0, len(pending), 8):
            batch = pending[offset:offset+8]
            vectors = await model.embed([r["text"] for r in batch])
            result = await session.run(Query("""
UNWIND $rows AS row MATCH (c:Chunk {id:row.id})
WHERE c.text_sha256=row.hash
SET c.embedding=row.vector, c.embedding_model=$model, c.embedding_digest=$digest,
c.embedding_dimensions=$dimensions, c.embedding_text_sha256=row.hash,
c.embedding_policy=$policy
RETURN count(c) AS count
""", timeout=10), rows=[{"id": r["id"], "hash": r["hash"], "vector": v} for r, v in zip(batch, vectors)],
                model=EMBED_MODEL, digest=EMBED_DIGEST, dimensions=DIMENSIONS, policy=EMBED_POLICY)
            count = (await result.single())["count"]
            if count != len(batch):
                raise ValueError("Chunk changed during embedding; rerun after ingestion stops")
            written += count
        await (await session.run(Query("""
CREATE VECTOR INDEX chunk_nomic_v1 IF NOT EXISTS FOR (c:Chunk) ON (c.embedding)
OPTIONS {indexConfig: {`vector.dimensions`:768, `vector.similarity_function`:'cosine'}}
""", timeout=30))).consume()
        await (await session.run(Query("CALL db.awaitIndex($name, 60)", timeout=65), name=INDEX)).consume()
        result = await session.run(
            "SHOW VECTOR INDEXES YIELD name,state,populationPercent WHERE name=$name "
            "RETURN name,state,populationPercent", name=INDEX)
        index_state = dict(await result.single())
    return {"chunks": len(rows), "written": written, "reused": len(rows)-written,
            "model": EMBED_MODEL, "digest": EMBED_DIGEST, "dimensions": DIMENSIONS,
            "index": index_state, "seconds": round(time.perf_counter()-start, 3)}


async def main():
    """Separate privileged CLI; the agent cannot call this module."""
    settings = Settings.from_environment()
    async with AsyncGraphDatabase.driver(settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password.get_secret_value())) as driver:
        async with httpx.AsyncClient(base_url=settings.ollama_url, trust_env=False) as client:
            print(json.dumps(await prepare(driver, Ollama(client, settings)), indent=2))


if __name__ == "__main__":
    asyncio.run(main())
