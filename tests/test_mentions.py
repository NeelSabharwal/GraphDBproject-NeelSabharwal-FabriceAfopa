"""Synthetic occurrence fixtures; never alter the reviewed research graph."""

from copy import deepcopy
import json
import uuid

from neo4j import GraphDatabase
import pytest

from app.config import Settings
from app.ingestion.documents import digest, normalize
from app.ingestion.reviews import ALIAS_ENTITIES
from app.mentions.graph import MentionImporter
from app.mentions.matcher import generate, pattern, rules, scope_reason, section_reason
from app.mentions.source import fingerprint, snapshot


@pytest.fixture
def mention_source():
    prefix = "test-mentions-" + uuid.uuid4().hex
    raw = "We selected Leiden for this synthetic system. Leiden supports this example.\nReferences\nLeiden citation."
    text, starts, ends = normalize(raw)
    page = dict(page=3, text=text, raw_text=raw, raw_starts=starts, raw_ends=ends, raw_sha256=digest(raw))
    chunk = dict(
        id=prefix + "c",
        paper_id=prefix + "p",
        text=text,
        text_sha256=digest(text),
        pdf_sha256=digest(prefix),
        page=3,
        start_char=0,
        end_char=len(text),
        page_raw_sha256=digest(raw),
    )
    aliases = {}
    entities = {}
    for alias, ident in ALIAS_ENTITIES.items():
        canonical = prefix + ident
        kind = {"method": "Method", "dataset": "Dataset", "task": "Task"}[ident.split(":")[0]]
        decision = dict(canonical_id=canonical, outcome="ACCEPT", decision="APPROVED", boundary="SYNTHETIC ONLY")
        aliases[alias] = decision
        entities[canonical] = dict(
            id=canonical,
            kind=kind,
            alias_decision_id=alias,
            resolution_status="STUDENT_APPROVED_SCOPED",
            alias_review_json=json.dumps(decision),
        )
    source = dict(
        chunks={chunk["id"]: chunk},
        entities=entities,
        decisions={"aliases": aliases},
        pages={chunk["paper_id"]: [page]},
    )
    # Matcher indexes PDF pages, so preserve page-number identity with unused preceding pages.
    source["pages"][chunk["paper_id"]] = [dict(page, page=1, raw_text=""), dict(page, page=2, raw_text=""), page]
    return source


def test_deterministic_source_matching_and_references(mention_source):
    candidates = generate(mention_source, rules())
    assert candidates == generate(deepcopy(mention_source), rules())
    assert sum(r["decision"] == "PROPOSED" for r in candidates) == 2
    assert candidates[-1]["reason"] == "REFERENCE_OR_POST_REFERENCE_ZONE"
    for row in candidates:
        chunk = mention_source["chunks"][row["chunk_id"]]
        assert chunk["text"][row["start_char"] : row["end_char"]] == row["surface"]


@pytest.mark.parametrize("value", ["dpr", "DPRx", "x-DPR", "DPR-large"])
def test_boundaries_do_not_expand_scientific_identity(value):
    assert pattern("DPR").search(value) is None


def test_aliases_do_not_merge_variants_or_louvain():
    assert pattern("WebQuestions").search("WebQuestionsSP") is None
    rule = next(r for r in rules() if r["surface"] == "Louvain")
    assert scope_reason(rule, "any", {}, 0, 7) == "REJECTED_EQUIVALENCE"


def test_labels_are_not_matcher_inputs(mention_source):
    expected = generate(mention_source, rules())
    mention_source["labels"] = {"synthetic": "arbitrary"}
    assert generate(mention_source, rules()) == expected


def test_tampered_source_fails_before_proposals(mention_source):
    next(iter(mention_source["chunks"].values()))["text"] += "changed"
    with pytest.raises(ValueError, match="hash"):
        generate(mention_source, rules())


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("2.2 Retriever: DPR\nBody follows.", "NUMBERED_HEADING"),
        ("Fixed DPR\nBody follows.", "SHORT_LABEL_OR_UNCERTAIN_WRAP"),
        ("DPR\nFigure 1: Explanatory caption.", "PRE_CAPTION_REGION"),
        ("Question Passage received by DPR Passage retrieved by BM25", "TABLE_COLUMN_HEADER"),
    ],
)
def test_structural_nonprose_is_excluded(raw, expected):
    text, starts, ends = normalize(raw)
    page = dict(raw_text=raw, text=text, raw_starts=starts, raw_ends=ends)
    start = text.index("DPR")
    assert section_reason(page, 3, None, start, start + 3) == expected


@pytest.fixture
def live_mentions(mention_source):
    settings = Settings.from_environment()
    with GraphDatabase.driver(
        settings.neo4j_uri,
        auth=(settings.neo4j_user, settings.neo4j_password.get_secret_value()),
        max_transaction_retry_time=0,
    ) as driver:
        chunk = next(iter(mention_source["chunks"].values()))
        rows = [r for r in generate(mention_source, rules()) if r["decision"] == "PROPOSED"]
        entity = mention_source["entities"][rows[0]["entity_id"]]
        ids = [chunk["id"], chunk["paper_id"], entity["id"]]
        try:
            driver.execute_query(
                "CREATE (p:Paper {id:$paper,pdf_sha256:$hash}) "
                "CREATE (c:Chunk) SET c=$chunk CREATE (e:Entity) SET e=$entity "
                "CREATE (c)-[:PART_OF]->(p) "
                'CREATE (c)-[:MENTIONS {start_char:999,end_char:1000,origin:"SYNTHETIC_PREEXISTING"}]->(e)',
                paper=chunk["paper_id"],
                hash=chunk["pdf_sha256"],
                chunk=chunk,
                entity=entity,
            )
            yield MentionImporter(driver), driver, rows
        finally:
            driver.execute_query("MATCH (n) WHERE n.id IN $ids DETACH DELETE n", ids=ids)


@pytest.mark.integration
def test_atomic_import_replay_and_receipt_specific_rollback(live_mentions):
    importer, driver, rows = live_mentions
    before = snapshot(driver)
    receipt = importer.apply(rows, fingerprint(before))
    assert len(receipt["created_ids"]) == 2
    repeat = importer.apply(rows, fingerprint(snapshot(driver)))
    assert repeat["created_ids"] == [] and len(repeat["reused_ids"]) == 2
    assert importer.rollback(repeat) == {"removed": 0}
    assert importer.dry_run(rows)["proposed_new"] == 0
    assert importer.rollback(receipt) == {"removed": 2}
    assert snapshot(driver) == before


@pytest.mark.integration
def test_mid_write_failure_rolls_back_all_edges(live_mentions, monkeypatch):
    importer, driver, rows = live_mentions
    before = snapshot(driver)
    original = importer._create

    def fail(tx, row):
        original(tx, row)
        raise RuntimeError("SYNTHETIC failure after write")

    monkeypatch.setattr(importer, "_create", fail)
    with pytest.raises(RuntimeError):
        importer.apply(rows, fingerprint(before))
    assert snapshot(driver) == before


@pytest.mark.integration
@pytest.mark.parametrize(
    "field,value",
    [
        ("text_sha256", "wrong"),
        ("paper_id", "wrong"),
        ("entity_id", "missing"),
        ("start_char", -1),
        ("alias_id", "A17"),
    ],
)
def test_invalid_reference_rejects_atomically(live_mentions, field, value):
    importer, driver, rows = live_mentions
    before = snapshot(driver)
    bad = deepcopy(rows)
    bad[-1][field] = value
    with pytest.raises(ValueError):
        importer.apply(bad, fingerprint(before))
    assert snapshot(driver) == before


@pytest.mark.integration
def test_stale_fingerprint_and_conflicting_occurrence(live_mentions):
    importer, driver, rows = live_mentions
    with pytest.raises(ValueError, match="Stale"):
        importer.apply(rows, "stale")
    receipt = importer.apply(rows, fingerprint(snapshot(driver)))
    driver.execute_query(
        'MATCH ()-[m:MENTIONS {proposal_id:$id}]->() SET m.surface="tampered"', id=receipt["created_ids"][0]
    )
    before = snapshot(driver)
    with pytest.raises(ValueError, match="Conflicting"):
        importer.apply(rows, fingerprint(before))
    assert snapshot(driver) == before
