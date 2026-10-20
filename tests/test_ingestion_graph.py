"""Actual Neo4j tests with uniquely named, self-cleaning fixture records."""

import uuid

from neo4j import GraphDatabase
from neo4j.exceptions import ConstraintError
import pytest

from app.config import Settings
from app.ingestion.citations import POLICY
from app.ingestion.documents import digest
from app.ingestion.graph import EvidenceGraph

pytestmark = pytest.mark.integration


@pytest.fixture
def graph_fixture():
    """Delete only this test's UUID-scoped records; preserve the student's corpus."""
    config = Settings.from_environment()
    prefix = f"test-ingestion-{uuid.uuid4().hex}"
    driver = GraphDatabase.driver(config.neo4j_uri,
                                 auth=(config.neo4j_user, config.neo4j_password.get_secret_value()))
    graph = EvidenceGraph(driver)
    graph.ensure_schema()
    papers = [{"paper_id": prefix + suffix, "work_id": prefix + suffix, "version": "v1",
               "title": "Original fixture", "authors": ["Test Author"], "year": 2026,
               "pdf_url": "https://example.invalid/fixture", "pdf_access": {"sha256": "fixture"},
               "reuse_note": "Original test prose"} for suffix in ("-a", "-b")]
    ids = [p["paper_id"] for p in papers]
    try:
        driver.verify_connectivity()
        graph.register_papers(papers)
        yield driver, graph, ids
    finally:
        driver.execute_query(
            "MATCH (n) WHERE (n:Paper AND n.id IN $ids) OR n.paper_id IN $ids DETACH DELETE n", ids=ids)
        driver.close()


def fixture_records(ids):
    """Two ordered chunks, one unreviewed Topic and one verified fixture citation."""
    text = "Our fixture addresses retrieval. Target reference."
    chunks = [{"id": ids[0] + f"-chunk{i}", "paper_id": ids[0], "text": text,
               "text_sha256": digest(text), "page": i + 1, "ordinal": i} for i in range(2)]
    entity = {"id": ids[0] + "-topic", "paper_id": ids[0], "kind": "Topic",
              "canonical_name": "retrieval", "normalized_name": "retrieval",
              "resolution_status": "UNREVIEWED_PAPER_SCOPED", "chunk_id": chunks[0]["id"],
              "start_char": text.index("retrieval"), "end_char": text.index("retrieval") + len("retrieval")}
    base = {"paper_id": ids[0], "subject_id": ids[0], "chunk_id": chunks[0]["id"],
            "quote": text, "quote_sha256": digest(text), "start_char": 0, "end_char": len(text)}
    claims = [
        {**base, "id": ids[0] + "-citation", "object_id": ids[1], "predicate": "CITES",
         "status": "EXTRACTED", "origin": "BIBLIOGRAPHY_VALIDATOR", "location_policy": POLICY,
         "source_location_status": "SOURCE_LOCATED"},
        {**base, "id": ids[0] + "-claim", "object_id": entity["id"], "predicate": "ADDRESSES",
         "status": "EXTRACTED", "origin": "LLM"},
    ]
    return chunks, [entity], claims


def test_real_import_idempotency_direction_and_review_preservation(graph_fixture):
    driver, graph, ids = graph_fixture
    chunks, entities, claims = fixture_records(ids)
    graph.import_paper(ids[0], chunks, entities, claims, "FIXTURE")
    assert "CITES" not in graph.counts(ids)["relationships"]
    graph.review_claim(claims[0]["id"], "Fixture Student", "Reviewed original fixture source", approved=True)
    before = graph.counts(ids)
    fingerprint = graph.fingerprint(ids)
    graph.import_paper(ids[0], chunks, entities, claims, "FIXTURE")
    assert before == graph.counts(ids)
    assert fingerprint == graph.fingerprint(ids)
    assert before["nodes"] == {"Paper": 2, "Chunk": 2, "Entity": 1, "Topic": 1, "Claim": 2}
    assert before["relationships"] == {
        "CITES": 1, "MENTIONS": 1, "NEXT": 1, "OBJECT": 2, "PART_OF": 2, "SUBJECT": 2, "SUPPORTED_BY": 2}
    result, _, _ = driver.execute_query(
        "MATCH (a:Paper {id:$a})-[:CITES]->(b:Paper {id:$b}) RETURN b.id AS id", a=ids[0], b=ids[1])
    assert len(result) == 1
    reverse, _, _ = driver.execute_query(
        "MATCH (:Paper {id:$b})-[:CITES]->(:Paper {id:$a}) RETURN 1", a=ids[0], b=ids[1])
    assert reverse == []
    graph.review_claim(claims[0]["id"], "Fixture Student", "Rejecting fixture assertion", approved=False)
    graph.import_paper(ids[0], chunks, entities, claims, "FIXTURE")
    assert "CITES" not in graph.counts(ids)["relationships"]
    status, _, _ = driver.execute_query("MATCH (c:Claim {id:$id}) RETURN c.status AS status, c.reviewer AS reviewer",
                                        id=claims[0]["id"])
    assert dict(status[0]) == {"status": "REJECTED", "reviewer": "Fixture Student"}


@pytest.mark.parametrize("label", ["Paper", "Chunk", "Entity", "Claim"])
def test_uniqueness_constraints_reject_duplicates(graph_fixture, label):
    driver, graph, ids = graph_fixture
    graph.import_paper(ids[0], *fixture_records(ids), "FIXTURE")
    # label is an internal test constant, never an LLM or user-supplied query fragment.
    with pytest.raises(ConstraintError):
        driver.execute_query(f"MATCH (n:{label}) WHERE n.id STARTS WITH $prefix "
                             f"WITH n LIMIT 1 CREATE (duplicate:{label} {{id:n.id}})",
                             prefix=ids[0])


def test_invalid_quote_never_writes_claims(graph_fixture):
    _, graph, ids = graph_fixture
    chunks, entities, claims = fixture_records(ids)
    claims[0]["quote"] = "Invented evidence"
    with pytest.raises(ValueError, match="quote/hash"):
        graph.import_paper(ids[0], chunks, entities, claims, "FIXTURE")
    assert graph.counts(ids)["nodes"] == {"Paper": 2}


@pytest.mark.parametrize("reference", ["missing", "foreign_existing", "different_paper"])
def test_invalid_entity_source_rejects_entire_batch_before_writes(graph_fixture, reference):
    driver, graph, ids = graph_fixture
    chunks, entities, claims = fixture_records(ids)
    invalid = {**entities[0], "id": ids[0] + "-invalid", "chunk_id": ids[0] + "-absent"}
    if reference == "foreign_existing":
        invalid["chunk_id"] = ids[1] + "-foreign-chunk"
        driver.execute_query("CREATE (:Chunk {id:$id, paper_id:$paper})",
                             id=invalid["chunk_id"], paper=ids[1])
    elif reference == "different_paper":
        invalid.update(chunk_id=chunks[0]["id"], paper_id=ids[1])
    before = graph.fingerprint(ids)
    with pytest.raises(ValueError, match="Entity source chunk|different source paper"):
        graph.import_paper(ids[0], chunks, [*entities, invalid], claims, "FIXTURE")
    assert graph.fingerprint(ids) == before
    records, _, _ = driver.execute_query(
        "MATCH (n) WHERE n.paper_id=$id RETURN labels(n) AS labels", id=ids[0])
    assert records == []  # No chunks, valid entities, invalid entities or claims leaked through.


def test_lookup_indexes_present(graph_fixture):
    driver, _, _ = graph_fixture
    rows, _, _ = driver.execute_query("SHOW INDEXES YIELD name RETURN name")
    assert {"paper_work", "entity_lookup", "chunk_page", "claim_review"} <= {row["name"] for row in rows}


def test_missing_citation_target_rolls_back_import(graph_fixture):
    _, graph, ids = graph_fixture
    chunks, entities, claims = fixture_records(ids)
    claims[0]["object_id"] = "missing-fixture-target"
    with pytest.raises(ValueError, match="Register source"):
        graph.import_paper(ids[0], chunks, entities, claims, "FIXTURE")
    assert graph.counts(ids)["nodes"] == {"Paper": 2}


def test_legacy_automatic_approval_retains_evidence_pending_student_review(graph_fixture):
    driver, graph, ids = graph_fixture
    chunks, entities, claims = fixture_records(ids)
    graph.import_paper(ids[0], chunks, entities, claims, "FIXTURE")
    driver.execute_query(
        "MATCH (c:Claim {id:$id}) SET c.status='SOURCE_VERIFIED', c.review_policy=$policy, "
        "c.reviewer='automated-bibliography-validator', c.reviewed_at='2026-10-20'", id=claims[0]["id"], policy=POLICY)
    driver.execute_query("MATCH (a:Paper {id:$a}), (b:Paper {id:$b}) MERGE (a)-[:CITES]->(b)", a=ids[0], b=ids[1])
    graph.import_paper(ids[0], chunks, entities, claims, "FIXTURE")
    rows, _, _ = driver.execute_query("MATCH (c:Claim {id:$id}) RETURN properties(c) AS c", id=claims[0]["id"])
    claim = rows[0]["c"]
    assert claim["status"] == "EXTRACTED"
    assert claim["source_location_status"] == "SOURCE_LOCATED"
    assert claim["student_review_status"] == "pending"
    assert "automated-bibliography-validator" in claim["review_history"][0]
    assert "CITES" not in graph.counts(ids)["relationships"]
    assert graph.counts(ids)["nodes"]["Claim"] == 2
    fingerprint = graph.fingerprint(ids)
    graph.import_paper(ids[0], chunks, entities, claims, "FIXTURE")
    assert graph.fingerprint(ids) == fingerprint


@pytest.mark.parametrize("reviewer,note", [("", "checked"), ("automated-validator", "checked"), ("Student", "")])
def test_review_requires_named_human_and_explicit_note(graph_fixture, reviewer, note):
    _, graph, ids = graph_fixture
    with pytest.raises(ValueError, match="named human"):
        graph.review_claim(ids[0], reviewer, note, approved=True)


def test_source_verified_flag_alone_cannot_create_derived_citation(graph_fixture):
    driver, graph, ids = graph_fixture
    records = fixture_records(ids)
    graph.import_paper(ids[0], *records, "FIXTURE")
    driver.execute_query("MATCH (c:Claim {id:$id}) SET c.status='SOURCE_VERIFIED'", id=records[2][0]["id"])
    graph.import_paper(ids[0], *records, "FIXTURE")
    assert "CITES" not in graph.counts(ids)["relationships"]
