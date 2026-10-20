"""Required citation preflight and optional extraction behavior on original PDF fixtures."""

import csv
import json
import uuid
from unittest.mock import Mock

import httpx
from neo4j import GraphDatabase
from pypdf import PdfWriter
from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject
import pytest

from app.config import Settings
from app.ingestion.documents import digest, parse_pdf
from app.ingestion.graph import EvidenceGraph
from scripts import ingest


def write_citation(root, row):
    """Write only this test's temporary citation input."""
    with (root / "corpus/citation_evidence.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(row))
        writer.writeheader()
        writer.writerow(row)


@pytest.fixture
def synthetic_corpus(tmp_path, monkeypatch):
    """Two UUID-scoped original PDFs; real parser/hash/citation checks, no downloads."""
    prefix = "arxiv:pr2-" + uuid.uuid4().hex
    papers = []
    for name in ("source", "target"):
        work = prefix + "-" + name
        paper = {"paper_id": work + "v1", "work_id": work, "version": "v1", "short_name": name,
                 "title": "Original " + name.title(), "authors": ["Alice Example"], "year": 2026,
                 "pdf_url": "https://example.invalid/" + name + ".pdf", "reuse_note": "Original test prose",
                 "suggested_download_path": "data/raw/" + name + ".pdf"}
        text = ["arXiv:" + paper["paper_id"].removeprefix("arxiv:")]
        if name == "source":
            text += ["References", "[1] Alice Example. 2026. Original Target. arXiv:" +
                     (prefix + "-target").removeprefix("arxiv:") + "."]
        else:
            text += ["Original target fixture prose."]
        writer = PdfWriter()
        page = writer.add_blank_page(width=600, height=800)
        font = DictionaryObject({NameObject("/Type"): NameObject("/Font"),
                                 NameObject("/Subtype"): NameObject("/Type1"),
                                 NameObject("/BaseFont"): NameObject("/Helvetica")})
        page[NameObject("/Resources")] = DictionaryObject({NameObject("/Font"): DictionaryObject({
            NameObject("/F1"): writer._add_object(font)})})
        stream = DecodedStreamObject()
        stream.set_data(("BT /F1 10 Tf 12 TL 40 700 Td " +
                         " ".join("(" + line + ") Tj T*" for line in text) + " ET").encode())
        page[NameObject("/Contents")] = writer._add_object(stream)
        path = tmp_path / paper["suggested_download_path"]
        path.parent.mkdir(parents=True, exist_ok=True)
        writer.write(path)
        paper["pdf_access"] = {"sha256": digest(path.read_bytes()), "size_bytes": path.stat().st_size,
                               "page_count": 1}
        papers.append(paper)
    pages, _ = parse_pdf(tmp_path / papers[0]["suggested_download_path"], papers[0])
    raw = pages[0]["raw_text"]
    start = raw.index(papers[1]["title"])
    row = {"source_paper_id": papers[0]["paper_id"], "target_work_id": papers[1]["work_id"],
           "selected_target_paper_id": papers[1]["paper_id"], "relation": "CITES", "evidence_id": "TEST-REF",
           "source_pdf_sha256": papers[0]["pdf_access"]["sha256"], "source_pdf_url": papers[0]["pdf_url"],
           "pdf_page_1based": "1", "page_text_sha256": pages[0]["raw_sha256"],
           "title_start_char_0based": str(start), "title_end_char_exclusive": str(start + len(papers[1]["title"])),
           "target_version_as_cited": "unspecified", "reference_locator": "Reference [1]",
           "identity_resolution": "matching title/authors and explicit arXiv ID"}
    (tmp_path / "corpus").mkdir()
    (tmp_path / "corpus/corpus_manifest.json").write_text(json.dumps({"papers": papers}))
    write_citation(tmp_path, row)
    # Production still restricts its manifest to the three approved papers.
    monkeypatch.setattr(ingest, "prototype_manifest", lambda _root: papers)
    return tmp_path, papers, row


def assert_citation_failure(report, papers):
    """A required citation failure is a core error, never optional partial success."""
    assert report["import_status"] == report["overall_status"] == "FAILED"
    assert [p["import_status"] for p in report["papers"]] == ["FAILED", "NOT_STARTED"]
    assert report["extractions"] == []
    assert report["failures"] == [{"paper_id": papers[0]["paper_id"], "stage": "citation_validation",
                                    "evidence_id": "TEST-REF",
                                    "detail": "Citation page hash mismatch; offsets cannot be trusted"}]
    assert ingest.exit_code(report) == ingest.exit_code(report, require_extraction=True) == 1


def test_invalid_page_hash_aborts_before_database_or_model_access(synthetic_corpus, monkeypatch):
    root, papers, row = synthetic_corpus
    row["page_text_sha256"] = "0" * 64
    write_citation(root, row)
    driver = Mock(side_effect=AssertionError("Database must not be opened"))
    monkeypatch.setattr(ingest.GraphDatabase, "driver", driver)
    report = ingest.run(root, sample_per_paper=1)
    assert_citation_failure(report, papers)
    driver.assert_not_called()
    saved = list((root / "data/processed/ingestion").glob("*/report.json"))
    assert len(saved) == 1
    assert json.loads(saved[0].read_text()) == report


@pytest.fixture
def corpus_graph(synthetic_corpus):
    """Real Neo4j connection with cleanup strictly limited to temporary fixture IDs."""
    root, papers, row = synthetic_corpus
    settings = Settings.from_environment()
    ids = [p["paper_id"] for p in papers]
    with GraphDatabase.driver(settings.neo4j_uri,
                              auth=(settings.neo4j_user, settings.neo4j_password.get_secret_value())) as driver:
        graph = EvidenceGraph(driver)
        try:
            yield root, papers, row, graph, ids
        finally:
            driver.execute_query("MATCH (n) WHERE (n:Paper AND n.id IN $ids) OR n.paper_id IN $ids "
                                 "DETACH DELETE n", ids=ids)


@pytest.mark.integration
@pytest.mark.parametrize("existing_import", [False, True])
def test_invalid_citation_leaves_real_graph_unchanged(corpus_graph, existing_import):
    root, papers, row, graph, ids = corpus_graph
    if existing_import:
        success = ingest.run(root, sample_per_paper=0)
        assert success["import_status"] == "SUCCEEDED"
        assert success["counts"]["nodes"] == {"Paper": 2, "Chunk": 2, "Claim": 1}
        assert ingest.exit_code(success) == 0
    before = graph.fingerprint(ids)
    row["page_text_sha256"] = "invalid-hash"
    write_citation(root, row)
    report = ingest.run(root, sample_per_paper=1)
    assert_citation_failure(report, papers)
    assert graph.fingerprint(ids) == before  # No transaction starts; existing evidence also survives.


@pytest.mark.integration
def test_optional_model_failure_still_imports_valid_citation(corpus_graph, monkeypatch):
    root, _, _, graph, ids = corpus_graph
    original_client = httpx.Client

    def client(*args, **kwargs):
        if "base_url" in kwargs:
            kwargs["transport"] = httpx.MockTransport(lambda request: httpx.Response(503))
        return original_client(*args, **kwargs)

    monkeypatch.setattr(ingest.httpx, "Client", client)
    report = ingest.run(root, sample_per_paper=1)
    assert report["import_status"] == "SUCCEEDED"
    assert all(p["import_status"] == "SUCCEEDED" for p in report["papers"])
    assert report["overall_status"] == "PARTIAL_SUCCESS"
    assert report["extractions"][0]["stage"] == "model_availability"
    assert ingest.exit_code(report) == 0
    assert ingest.exit_code(report, require_extraction=True) == 2
    assert graph.counts(ids)["nodes"] == {"Paper": 2, "Chunk": 2, "Claim": 1}
