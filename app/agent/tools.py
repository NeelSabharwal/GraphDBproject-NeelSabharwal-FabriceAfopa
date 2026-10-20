"""The agent's entire database capability: fixed, bounded read templates."""

import hashlib
import re

from neo4j import Query

from app.agent.models import CitationPath, Evidence, ExpandEvidence, SearchChunks, SourceExcerpt
from app.agent.catalog import PaperReference
from app.agent.grounding import candidates
from app.agent.ollama import DIMENSIONS, EMBED_DIGEST, EMBED_MODEL, EMBED_POLICY, INDEX
from app.ingestion.graph import HUMAN_POLICY

TOOL_MODELS = {
    "search_chunks": (SearchChunks, "Find semantic evidence. Start here to discover real paper/chunk IDs."),
    "get_source_excerpt": (SourceExcerpt, "Read a returned chunk before citing it in an answer."),
    "find_citation_path": (CitationPath, "Find a directed student-approved citation chain; may be pending."),
    "expand_verified_evidence": (ExpandEvidence, "Find reviewed scientific claims and shared-entity evidence."),
}
TOOL_SCHEMAS = [{"type": "function", "function": {
    "name": name, "description": description, "parameters": model.model_json_schema(),
}} for name, (model, description) in TOOL_MODELS.items()]

# An additional early refusal, not the security boundary. There is NO raw query executor.
UNSAFE = re.compile(r"\b(detach\s+delete|delete\s+\w+|drop\s+(?:database|index|constraint)|"
                    r"create\s*\(|merge\s*\(|load\s+csv|apoc\.|dbms\.|set\s+\w+\.)", re.I)
APPROVED = ("c.status='SOURCE_VERIFIED' AND c.human_reviewed=true "
            "AND c.student_review_status='approved' AND c.review_policy=$policy "
            "AND trim(coalesce(c.reviewer,''))<>'' AND c.reviewed_at IS NOT NULL")
EVIDENCE_RETURN = """
RETURN chunk.id AS chunk_id, p.id AS paper_id, p.title AS title, chunk.page AS page,
chunk.text AS text, chunk.text_sha256 AS text_sha256, p.pdf_sha256 AS pdf_sha256,
chunk.page_raw_sha256 AS page_raw_sha256, p.source_url AS source_url,
p.source_version AS source_version, chunk.start_char AS start_char,
chunk.end_char AS end_char, chunk.parser_version AS parser_version,
chunk.chunker_version AS chunker_version
"""
PATH_QUERY = """
MATCH path=(source:Paper {id:$source})-[:CITES*1..3]->(target:Paper {id:$target})
WHERE length(path)<=$hops AND all(r IN relationships(path) WHERE EXISTS {
 MATCH (c:Claim {predicate:'CITES'})-[:SUBJECT]->(a:Paper),
       (c)-[:OBJECT]->(b:Paper), (c)-[:SUPPORTED_BY]->(:Chunk)
 WHERE c.id IN r.claim_ids AND a=startNode(r) AND b=endNode(r) AND """ + APPROVED + """
})
RETURN [p IN nodes(path) | p.id] AS papers,
       [r IN relationships(path) | r.claim_ids] AS edge_claim_ids
ORDER BY length(path), papers LIMIT 1
"""


def validate_call(name, arguments):
    """No unknown operations, hidden query fields or coercible unbounded values."""
    if name not in TOOL_MODELS:
        raise ValueError("Unknown or unsafe tool")
    return TOOL_MODELS[name][0].model_validate(arguments)


def validate_evidence(row):
    """Detect stale/corrupt source text before returning it as evidence."""
    evidence = Evidence.model_validate(row)
    if (hashlib.sha256(evidence.text.encode()).hexdigest() != evidence.text_sha256
            or evidence.end_char - evidence.start_char != len(evidence.text)):
        raise ValueError("Stored evidence hash/coordinates do not match")
    return evidence.model_dump()


class RetrievalTools:
    """Bounded read-only operations; no ingestion or arbitrary-Cypher entry point."""

    def __init__(self, driver, ollama, settings):
        self.driver, self.ollama, self.settings = driver, ollama, settings

    async def read(self, query, **parameters):
        """READ routing plus fixed templates; Community has no separate read role."""
        async with self.driver.session(default_access_mode="READ") as session:
            result = await session.run(Query(query, timeout=self.settings.agent_query_timeout), **parameters)
            return [dict(row) async for row in result]

    async def paper(self, paper_id):
        """Reject even well-shaped IDs unless the paper exists."""
        if not await self.read("MATCH (p:Paper {id:$id}) RETURN p.id AS id", id=paper_id):
            raise ValueError("Unknown Paper ID")

    async def catalog(self):
        """Bounded identity metadata only; reject overflow rather than hide ambiguity."""
        rows = await self.read(
            "MATCH (p:Paper) RETURN p.id AS id,p.title AS title,"
            "coalesce(properties(p).aliases,[]) AS aliases ORDER BY p.id LIMIT 65")
        if len(rows) > 64:
            raise ValueError("Paper catalog exceeds the 64-paper resolution budget")
        return [PaperReference.model_validate(row).model_dump() for row in rows]

    async def execute(self, name, arguments):
        """Dispatch only after strict schema validation."""
        args = validate_call(name, arguments)
        return await getattr(self, name)(args)

    async def search_chunks(self, args):
        """Bounded ANN candidates followed by provenance/model/optional-paper checks."""
        if args.paper_id:
            await self.paper(args.paper_id)
        rows = await self.read(
            "SHOW VECTOR INDEXES YIELD name,state,options,labelsOrTypes,properties WHERE name=$name "
            "RETURN state,options,labelsOrTypes,properties", name=INDEX)
        if not rows or rows[0]["state"] != "ONLINE":
            raise ValueError("Vector index unavailable; run make embed")
        config = rows[0]["options"]["indexConfig"]
        if (rows[0]["labelsOrTypes"] != ["Chunk"] or rows[0]["properties"] != ["embedding"]
                or config.get("vector.dimensions") != DIMENSIONS
                or str(config.get("vector.similarity_function")).lower() != "cosine"):
            raise ValueError("Incompatible vector index")
        vector = (await self.ollama.embed([args.query], query=True))[0]
        rows = await self.read("""
CALL db.index.vector.queryNodes($index, $candidates, $vector) YIELD node, score
MATCH (node)-[:PART_OF]->(p:Paper)
WHERE node.paper_id=p.id AND node.embedding_model=$model AND node.embedding_digest=$digest
AND node.embedding_dimensions=$dimensions AND node.embedding_policy=$embedding_policy
AND node.embedding_text_sha256=node.text_sha256 AND ($paper IS NULL OR p.id=$paper)
RETURN node.id AS chunk_id, p.id AS paper_id, p.title AS title, node.page AS page,
       substring(node.text,0,300) AS preview, score
ORDER BY score DESC, chunk_id LIMIT $limit
""", index=INDEX, candidates=64, vector=vector, model=EMBED_MODEL, digest=EMBED_DIGEST,
            dimensions=DIMENSIONS, embedding_policy=EMBED_POLICY, paper=args.paper_id, limit=args.top_k)
        # Search results include authentic complete provenance for the trace, but must
        # still be explicitly read by get_source_excerpt before answer citation.
        evidence = [await self.excerpt(row["chunk_id"]) for row in rows]
        # Better discovery previews, not answer context: explicit reads remain mandatory.
        for row, source in zip(rows, evidence):
            choices = candidates(args.query, {source["chunk_id"]: source})
            if choices:
                row["preview"] = choices[0]["quote"]
        return {"status": "ok" if rows else "unavailable", "matches": rows,
                "evidence": evidence, "paths": [], "candidate_limit": 64}

    async def excerpt(self, chunk_id):
        """Identity and source provenance are always assigned from real graph records."""
        rows = await self.read(
            "MATCH (chunk:Chunk {id:$id})-[:PART_OF]->(p:Paper) "
            "WHERE chunk.paper_id=p.id AND chunk.pdf_sha256=p.pdf_sha256 " + EVIDENCE_RETURN, id=chunk_id)
        if len(rows) != 1:
            raise ValueError("Unknown or inconsistent Chunk ID")
        return validate_evidence(rows[0])

    async def get_source_excerpt(self, args):
        """No model-provided page number or filesystem/URL fetching."""
        return {"status": "ok", "evidence": [await self.excerpt(args.chunk_id)], "paths": []}

    async def claim_supports(self, ids):
        """Revalidate human approval and exact quote support at traversal time."""
        rows = await self.read("""
MATCH (c:Claim)-[:SUBJECT]->(subject), (c)-[:OBJECT]->(object),
      (c)-[support:SUPPORTED_BY]->(chunk:Chunk)
WHERE c.id IN $ids AND """ + APPROVED + """
RETURN c.id AS claim_id, c.predicate AS predicate, subject.id AS subject_id,
       object.id AS object_id, chunk.id AS chunk_id, support.quote AS quote,
       support.start_char AS start_char, support.end_char AS end_char,
       support.quote_sha256 AS quote_sha256
ORDER BY claim_id LIMIT 24
""", ids=ids, policy=HUMAN_POLICY)
        evidence, claims = {}, []
        for row in rows:
            chunk = await self.excerpt(row["chunk_id"])
            start, end = row["start_char"], row["end_char"]
            if (chunk["paper_id"] != row["subject_id"]
                    or not isinstance(start, int) or not isinstance(end, int)
                    or not 0 <= start < end <= len(chunk["text"])
                    or chunk["text"][start:end] != row["quote"]
                    or hashlib.sha256(row["quote"].encode()).hexdigest() != row["quote_sha256"]):
                raise ValueError("Reviewed claim source support is invalid")
            evidence[chunk["chunk_id"]] = chunk
            claims.append({**row, "status": "SOURCE_VERIFIED"})
        return list(evidence.values()), claims

    async def find_citation_path(self, args):
        """Validate every derived edge against an approved, source-supported claim."""
        await self.paper(args.source_id)
        await self.paper(args.target_id)
        rows = await self.read(PATH_QUERY, source=args.source_id, target=args.target_id,
                               hops=args.max_hops, policy=HUMAN_POLICY)
        if not rows:
            return {"status": "unavailable", "evidence": [], "paths": [],
                    "limitation": "No approved directed path within the hop limit; pending claims are excluded."}
        path = rows[0]
        ids = sorted({cid for group in path["edge_claim_ids"] for cid in group})
        evidence, claims = await self.claim_supports(ids)
        edges = []
        for source, target, group in zip(path["papers"], path["papers"][1:], path["edge_claim_ids"]):
            support = [c for c in claims if c["claim_id"] in group and c["subject_id"] == source
                       and c["object_id"] == target and c["predicate"] == "CITES"]
            if not support:
                raise ValueError("Citation path approval changed or support missing")
            edges.append({"source": source, "target": target, "claims": support})
        return {"status": "ok", "evidence": evidence,
                "paths": [{"type": "CITES", "papers": path["papers"], "edges": edges}]}

    async def expand_verified_evidence(self, args):
        """One reviewed entity join; no alias guessing or unreviewed mentions."""
        await self.paper(args.paper_id)
        rows = await self.read("""
MATCH (seed:Claim)-[:SUBJECT]->(:Paper {id:$id}), (seed)-[:OBJECT]->(entity:Entity)
WHERE seed.predicate IN ['USES','EVALUATED_ON','ADDRESSES']
AND seed.status='SOURCE_VERIFIED' AND seed.human_reviewed=true
AND seed.student_review_status='approved' AND seed.review_policy=$policy
AND trim(coalesce(seed.reviewer,''))<>'' AND seed.reviewed_at IS NOT NULL
MATCH (c:Claim)-[:OBJECT]->(entity), (c)-[:SUBJECT]->(p:Paper), (c)-[:SUPPORTED_BY]->(:Chunk)
WHERE c.predicate IN ['USES','EVALUATED_ON','ADDRESSES'] AND """ + APPROVED + """
RETURN DISTINCT seed.id AS seed_id, c.id AS claim_id, entity.id AS entity_id
ORDER BY seed_id, claim_id LIMIT $limit
""", id=args.paper_id, limit=args.limit, policy=HUMAN_POLICY)
        if not rows:
            return {"status": "unavailable", "evidence": [], "paths": [],
                    "limitation": "No student-approved scientific relationships available."}
        ids = sorted({row[key] for row in rows for key in ("seed_id", "claim_id")})
        evidence, claims = await self.claim_supports(ids)
        if set(ids) != {c["claim_id"] for c in claims}:
            raise ValueError("Scientific review changed or source support missing")
        return {"status": "ok", "evidence": evidence,
                "paths": [{"type": "VERIFIED_ENTITY", "joins": rows, "claims": claims}]}
