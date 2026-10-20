"""Real Neo4j retrieval checks; fixture writes are isolated and cleaned by UUID."""

import asyncio
import hashlib
import uuid

import httpx
import pytest
from neo4j import AsyncGraphDatabase, GraphDatabase

from app.agent.ollama import Ollama
from app.agent.tools import RetrievalTools
from app.agent.workflow import validate_output_citation
from app.agent.catalog import resolve_direction, resolve_name
from app.config import Settings
from app.ingestion.graph import HUMAN_POLICY
from scripts.embed_chunks import prepare

pytestmark = pytest.mark.integration


async def with_tools(operation):
    """Run one bounded operation against actual Compose dependencies."""
    config = Settings.from_environment()
    async with AsyncGraphDatabase.driver(config.neo4j_uri,
            auth=(config.neo4j_user, config.neo4j_password.get_secret_value())) as driver:
        async with httpx.AsyncClient(base_url=config.ollama_url, trust_env=False) as client:
            model = Ollama(client, config)
            return await operation(RetrievalTools(driver, model, config))


def test_real_semantic_retrieval_and_idempotent_embeddings():
    async def exercise(tools):
        result = await tools.execute("search_chunks", {
            "query": "DPR dense passage retrieval two encoders dot product similarity",
            "paper_id": "arxiv:2004.04906v1", "top_k": 4})
        assert result["status"] == "ok"
        assert 1 <= len(result["evidence"]) <= 4
        assert all(e["paper_id"] == "arxiv:2004.04906v1" for e in result["evidence"])
        assert all(e["page"] > 0 and len(e["pdf_sha256"]) == 64 for e in result["evidence"])
        assert any("dot product" in e["text"] or "encoders" in e["text"] for e in result["evidence"])
        for source in result["evidence"]:
            read = await tools.execute("get_source_excerpt", {"chunk_id": source["chunk_id"]})
            assert read["evidence"] == [source]
        report = await prepare(tools.driver, tools.ollama)
        assert report["written"] == 0
        assert report["reused"] >= 153
        assert report["index"]["state"] == "ONLINE"
    asyncio.run(with_tools(exercise))


def test_q15_forged_page_against_actual_dpr_evidence():
    """Synthetic output only; no PDF, graph property or gold fixture is changed."""
    async def exercise(tools):
        source = await tools.excerpt(
            "651d3ede4b76912d5aa04aecd2e6a7a4e42008cf3447e928cd13290d584eed0d")
        assert source["paper_id"] == "arxiv:2004.04906v1"
        assert source["page"] == 3
        evidence = {source["chunk_id"]: source}
        with pytest.raises(ValueError, match="paper/page"):
            validate_output_citation(
                {"paper_id": "arxiv:2004.04906v1", "pdf_page_1based": 999}, evidence)
        validate_output_citation(
            {"paper_id": source["paper_id"], "pdf_page_1based": source["page"]}, evidence)
    asyncio.run(with_tools(exercise))


def test_real_catalog_resolves_direction_without_vector_discovery():
    async def exercise(tools):
        catalog = await tools.catalog()
        endpoints = resolve_direction("GraphRAG to DPR", catalog)
        assert endpoints == {"source_id": "arxiv:2404.16130v1", "target_id": "arxiv:2004.04906v1"}
        result = await tools.execute("find_citation_path", {**endpoints, "max_hops": 2})
        assert result["status"] == "unavailable"
        assert result["paths"] == []
        reverse = resolve_direction("DPR to GraphRAG", catalog)
        assert reverse["source_id"] == endpoints["target_id"]
        assert reverse["target_id"] == endpoints["source_id"]
        with pytest.raises(ValueError, match="unsupported"):
            resolve_name("Nonexistent paper", catalog)
    asyncio.run(with_tools(exercise))


@pytest.fixture
def fixture_graph():
    """Original synthetic prose and review metadata, never real student approval."""
    config = Settings.from_environment()
    prefix = "test-agent-" + uuid.uuid4().hex
    ids = [prefix + suffix for suffix in ("-a", "-b", "-c")]
    text = "Original synthetic citation support for retrieval tests."
    hash_value = hashlib.sha256(text.encode()).hexdigest()
    with GraphDatabase.driver(config.neo4j_uri,
            auth=(config.neo4j_user, config.neo4j_password.get_secret_value())) as driver:
        try:
            driver.execute_query("""
UNWIND $ids AS id CREATE (p:Paper {id:id, title:'Synthetic fixture', pdf_sha256:'fixture',
source_url:'https://example.invalid', source_version:'v1'})
CREATE (chunk:Chunk {id:id+'-chunk', paper_id:id, text:$text, text_sha256:$hash,
pdf_sha256:'fixture', page_raw_sha256:'fixture', page:1, start_char:0, end_char:size($text),
parser_version:'fixture', chunker_version:'fixture'})-[:PART_OF]->(p)
""", ids=ids, text=text, hash=hash_value)
            driver.execute_query("""
UNWIND [0,1] AS i MATCH (a:Paper {id:$ids[i]}), (b:Paper {id:$ids[i+1]}),
(chunk:Chunk {id:$ids[i]+'-chunk'})
CREATE (c:Claim {id:$ids[i]+'-claim', paper_id:a.id, predicate:'CITES',
status:'SOURCE_VERIFIED', human_reviewed:true, student_review_status:'approved',
review_policy:$policy, reviewer:'SYNTHETIC TEST ONLY', reviewed_at:'fixture'})
CREATE (c)-[:SUBJECT]->(a), (c)-[:OBJECT]->(b),
(c)-[:SUPPORTED_BY {quote:$text,quote_sha256:$hash,start_char:0,end_char:size($text)}]->(chunk),
(a)-[:CITES {claim_ids:[c.id]}]->(b)
""", ids=ids, policy=HUMAN_POLICY, text=text, hash=hash_value)
            yield driver, ids
        finally:
            driver.execute_query(
                "MATCH (n) WHERE n.id IN $ids OR n.paper_id IN $ids DETACH DELETE n", ids=ids)


def test_real_directed_paths_depth_and_pending_exclusion(fixture_graph):
    driver, ids = fixture_graph
    async def exercise(tools):
        base = {"source_id": ids[0], "target_id": ids[2]}
        result = await tools.execute("find_citation_path", base)
        assert result["paths"][0]["papers"] == ids
        assert len(result["evidence"]) == 2
        assert all(c["status"] == "SOURCE_VERIFIED"
                   for edge in result["paths"][0]["edges"] for c in edge["claims"])
        assert (await tools.execute("find_citation_path", {**base, "max_hops": 1}))["paths"] == []
        assert (await tools.execute("find_citation_path",
            {"source_id": ids[2], "target_id": ids[0]}))["paths"] == []
    asyncio.run(with_tools(exercise))
    # A stale derived edge and even SOURCE_VERIFIED status must not bypass approval.
    driver.execute_query("MATCH (c:Claim {id:$id}) SET c.human_reviewed=false",
                         id=ids[1]+"-claim")
    async def pending(tools):
        result = await tools.execute("find_citation_path", {"source_id": ids[0], "target_id": ids[2]})
        assert result["status"] == "unavailable" and result["paths"] == []
    asyncio.run(with_tools(pending))


def test_real_verified_scientific_expansion_and_corrupt_support(fixture_graph):
    driver, ids = fixture_graph
    driver.execute_query("""
MATCH (c:Claim {id:$id}), (c)-[old:OBJECT]->(:Paper) DELETE old
CREATE (e:Entity {id:$entity,paper_id:$paper,kind:'Method'})
CREATE (c)-[:OBJECT]->(e) SET c.predicate='USES'
""", id=ids[0]+"-claim", entity=ids[0]+"-entity", paper=ids[0])
    async def valid(tools):
        result = await tools.execute("expand_verified_evidence", {"paper_id": ids[0]})
        assert result["paths"][0]["claims"][0]["predicate"] == "USES"
        assert result["evidence"][0]["paper_id"] == ids[0]
    asyncio.run(with_tools(valid))
    driver.execute_query("MATCH (:Claim {id:$id})-[s:SUPPORTED_BY]->() SET s.quote='forged'",
                         id=ids[0]+"-claim")
    async def corrupt(tools):
        with pytest.raises(ValueError, match="source support"):
            await tools.execute("expand_verified_evidence", {"paper_id": ids[0]})
    asyncio.run(with_tools(corrupt))


@pytest.mark.parametrize("name,args", [
    ("get_source_excerpt", {"chunk_id": "not-a-real-chunk"}),
    ("search_chunks", {"query": "text", "paper_id": "invented"}),
    ("find_citation_path", {"source_id": "invented", "target_id": "also-invented"}),
    ("expand_verified_evidence", {"paper_id": "invented"}),
])
def test_nonexistent_graph_identities_rejected(name, args):
    async def exercise(tools):
        with pytest.raises(ValueError, match="Unknown"):
            await tools.execute(name, args)
    asyncio.run(with_tools(exercise))
