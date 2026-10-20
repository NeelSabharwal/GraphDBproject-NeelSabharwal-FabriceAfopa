"""Deterministic ingestion tests using generated original text, never paper binaries."""

from copy import deepcopy
import json

import httpx
import pytest
from pypdf import PdfWriter
from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject

from app.ingestion.citations import verify_citation
from app.ingestion.documents import (
    digest, download_pdf, make_chunks, normalize, parse_pdf, prototype_manifest, save_pdf, verify_pdf,
)
from app.ingestion.extraction import extract_sample, ollama_schema, validate_extraction
from app.ingestion.graph import validate_claims


@pytest.fixture
def paper_pdf(tmp_path):
    """Generate two simple PDF pages with original test prose and an identity marker."""
    writer = PdfWriter()
    for text in ("arXiv:2004.04906v1 Test paper uses Widget method.", "Second page has original test text."):
        page = writer.add_blank_page(width=600, height=800)
        font = DictionaryObject({NameObject("/Type"): NameObject("/Font"),
                                 NameObject("/Subtype"): NameObject("/Type1"),
                                 NameObject("/BaseFont"): NameObject("/Helvetica")})
        page[NameObject("/Resources")] = DictionaryObject({
            NameObject("/Font"): DictionaryObject({NameObject("/F1"): writer._add_object(font)})})
        stream = DecodedStreamObject()
        stream.set_data(f"BT /F1 12 Tf 50 700 Td ({text}) Tj ET".encode())
        page[NameObject("/Contents")] = writer._add_object(stream)
    path = tmp_path / "test.pdf"
    writer.write(path)
    paper = {"paper_id": "arxiv:2004.04906v1", "work_id": "arxiv:2004.04906", "version": "v1",
             "pdf_access": {"sha256": digest(path.read_bytes()), "size_bytes": path.stat().st_size,
                            "page_count": 2}}
    return path, paper


def test_real_pdf_parser_pages_hashes_and_deterministic_chunks(paper_pdf):
    """Exercise the actual parser, page provenance and repeatable chunk construction."""
    path, paper = paper_pdf
    pages, problems = parse_pdf(path, paper)
    assert problems == []
    assert [p["page"] for p in pages] == [1, 2]
    assert "Second page" in pages[1]["raw_text"]
    chunks = make_chunks(paper, pages)
    assert chunks == make_chunks(paper, parse_pdf(path, paper)[0])
    assert len({c["id"] for c in chunks}) == 2
    for chunk in chunks:
        page = pages[chunk["page"] - 1]
        assert chunk["text"] == page["text"][chunk["start_char"]:chunk["end_char"]]
        assert digest(chunk["text"]) == chunk["text_sha256"]
        assert chunk["paper_id"] == paper["paper_id"]
        assert chunk["page_raw_sha256"] == digest(page["raw_text"])


def test_normalization_retains_ligature_whitespace_locations():
    text, starts, ends = normalize("A  \nﬁ\tB")
    assert text == "A fi B"
    assert starts == [0, 1, 4, 4, 5, 6]
    assert ends == [1, 4, 5, 5, 6, 7]


def test_long_chunks_cover_page_without_crossing_or_losing_text(paper_pdf):
    _, paper = paper_pdf
    raw = "word ﬁ more words\n" * 400
    text, starts, ends = normalize(raw)
    page = {"page": 7, "page_label": "5", "text": text, "raw_sha256": digest(raw),
            "raw_starts": starts, "raw_ends": ends}
    chunks = make_chunks(paper, [page])
    assert len(chunks) > 2
    assert all(c["page"] == 7 and len(c["text"]) <= 1400 for c in chunks)
    assert chunks[0]["start_char"] == 0 and chunks[-1]["end_char"] == len(text)
    assert all(b["start_char"] < a["end_char"] for a, b in zip(chunks, chunks[1:]))
    changed = deepcopy(paper)
    changed["pdf_access"]["sha256"] = "another-hash"
    assert make_chunks(changed, [page])[0]["id"] != chunks[0]["id"]


@pytest.mark.parametrize("change", ["checksum", "page_count", "identity"])
def test_pdf_validation_rejects_wrong_pinned_source(paper_pdf, change):
    path, paper = paper_pdf
    if change == "checksum":
        paper["pdf_access"]["sha256"] = "0" * 64
    elif change == "page_count":
        paper["pdf_access"]["page_count"] = 3
    else:
        paper["paper_id"] = "arxiv:2004.04906v2"
    with pytest.raises(ValueError):
        parse_pdf(path, paper)


def test_non_pdf_rejected(paper_pdf):
    with pytest.raises(ValueError, match="Expected a PDF"):
        verify_pdf(b"<html>Error</html>", paper_pdf[1])


def test_parser_empty_page_is_recorded(paper_pdf, monkeypatch):
    from pypdf._page import PageObject
    original = PageObject.extract_text

    def empty_second(page, *args, **kwargs):
        text = original(page, *args, **kwargs)
        return "" if "Second page" in text else text

    monkeypatch.setattr(PageObject, "extract_text", empty_second)
    pages, problems = parse_pdf(*paper_pdf)
    assert len(pages) == 2
    assert {"page": 2, "kind": "empty_page"} in problems


def test_download_failure_does_not_create_or_replace_file(tmp_path, paper_pdf):
    _, paper = paper_pdf
    paper.update(pdf_url="https://arxiv.org/pdf/2004.04906v1", suggested_download_path="data/raw/test.pdf")
    with httpx.Client(transport=httpx.MockTransport(
        lambda request: httpx.Response(200, content=b"%PDF-wrong", headers={"content-type": "application/pdf"})
    )) as client:
        with pytest.raises(ValueError, match="checksum mismatch"):
            download_pdf(tmp_path, paper, client)
        assert not (tmp_path / paper["suggested_download_path"]).exists()
        target = tmp_path / paper["suggested_download_path"]
        target.parent.mkdir(parents=True)
        target.write_bytes(b"%PDF-existing")
        with pytest.raises(ValueError):
            download_pdf(tmp_path, paper, client)
        assert target.read_bytes() == b"%PDF-existing"


def test_manifest_rejects_unapproved_prototype(tmp_path):
    (tmp_path / "corpus").mkdir()
    (tmp_path / "corpus/corpus_manifest.json").write_text(json.dumps({
        "papers": [{"selection_stage": "prototype", "paper_id": "arxiv:unapproved"}]}))
    with pytest.raises(ValueError, match="exactly the three"):
        prototype_manifest(tmp_path)


@pytest.mark.parametrize("failure", ["interrupted_write", "publish", "short_write"])
def test_atomic_save_failure_preserves_valid_pdf_and_cleans_temporary(paper_pdf, monkeypatch, failure):
    import app.ingestion.documents as documents
    path, paper = paper_pdf
    previous = path.read_bytes()

    def fail(*_args):
        raise OSError("simulated interrupted save")

    if failure == "interrupted_write":
        monkeypatch.setattr(documents.os, "fsync", fail)
    elif failure == "publish":
        monkeypatch.setattr(documents.os, "replace", fail)
    else:
        monkeypatch.setattr(documents.os, "fsync", lambda fd: documents.os.ftruncate(fd, 10))
    with pytest.raises((OSError, ValueError)):
        save_pdf(path, previous, paper)
    assert path.read_bytes() == previous
    assert list(path.parent.glob(f".{path.name}.*.tmp")) == []


def test_download_atomically_publishes_complete_pdf(tmp_path, paper_pdf):
    original, paper = paper_pdf
    data = original.read_bytes()
    paper.update(pdf_url="https://example.invalid/fixture", suggested_download_path="data/raw/download.pdf")
    with httpx.Client(transport=httpx.MockTransport(
        lambda request: httpx.Response(200, content=data, headers={"content-type": "application/pdf"})
    )) as client:
        path = download_pdf(tmp_path, paper, client)
    assert path.read_bytes() == data
    assert list(path.parent.iterdir()) == [path]


@pytest.fixture
def extraction_case():
    chunk = {"id": "chunk", "paper_id": "paper", "text": "Our paper uses Widget for question answering."}
    output = {"entities": [{"name": "Widget", "kind": "Method"}],
              "relations": [{"predicate": "USES", "object_name": "Widget",
                             "quote": chunk["text"], "qualifiers": "Author assertion; not independently true"}]}
    model = {"name": "test-model", "digest": "test-digest"}
    return chunk, output, model


def test_valid_extraction_stays_unreviewed(extraction_case):
    chunk, output, model = extraction_case
    entities, claims = validate_extraction(json.dumps(output), chunk, model)
    assert claims[0]["status"] == "EXTRACTED"
    assert claims[0]["origin"] == "LLM"
    assert claims[0]["model_digest"] == model["digest"]
    assert claims[0]["qualifiers"] == output["relations"][0]["qualifiers"]
    validate_claims([chunk], entities, claims)
    claims[0]["status"] = "SOURCE_VERIFIED"
    with pytest.raises(ValueError, match="remain EXTRACTED"):
        validate_claims([chunk], entities, claims)


@pytest.mark.parametrize("mutation", ["missing_chunk", "missing_chunk_id", "different_paper"])
def test_entity_requires_same_paper_source_chunk_even_without_claims(extraction_case, mutation):
    chunk, output, model = extraction_case
    entities, _ = validate_extraction(json.dumps(output), chunk, model)
    if mutation == "missing_chunk":
        entities[0]["chunk_id"] = "absent"
    elif mutation == "missing_chunk_id":
        del entities[0]["chunk_id"]
    else:
        entities[0]["paper_id"] = "another-paper"
    with pytest.raises(ValueError, match="Entity source chunk"):
        validate_claims([chunk], entities, [])


@pytest.mark.parametrize("mutation", ["not_json", "list", "status", "quote", "entity", "range", "unknown", "too_many"])
def test_malformed_or_unsupported_extraction_is_rejected(extraction_case, mutation):
    chunk, output, model = extraction_case
    if mutation == "status":
        output["relations"][0]["status"] = "SOURCE_VERIFIED"
    elif mutation == "quote":
        output["relations"][0]["quote"] = "Widget was invented in 1900."
    elif mutation == "entity":
        output["entities"][0]["name"] = "Invented"
    elif mutation == "range":
        output["entities"][0]["kind"] = "Dataset"
    elif mutation == "unknown":
        output["relations"][0]["object_name"] = "Missing"
    elif mutation == "too_many":
        output["entities"] *= 3
    content = "invalid" if mutation == "not_json" else "[]" if mutation == "list" else json.dumps(output)
    with pytest.raises(ValueError):
        validate_extraction(content, chunk, model)


@pytest.mark.parametrize("payload", [None, [], {}, {"message": []}, {"message": {"content": ""}},
                                   {"message": {"content": "{}"}, "done": False}])
def test_malformed_ollama_preserves_failure(extraction_case, payload):
    chunk, _, model = extraction_case
    with httpx.Client(base_url="http://test", transport=httpx.MockTransport(
        lambda request: httpx.Response(200, content=json.dumps(payload), headers={"content-type": "application/json"})
    )) as client:
        result = extract_sample(client, chunk, model)
    assert result["status"] == "FAILED"
    assert result["error"] == "ValueError"
    assert result["response"] == payload
    assert result["wall_seconds"] >= 0


@pytest.fixture
def citation_case():
    raw = "References\n[22] Alice Example. 2020. A Test Retrieval Method. arXiv:1234.56789.\n"
    title = "A Test Retrieval Method"
    start, end = raw.index(title), raw.index(title) + len(title)
    source = {"paper_id": "source", "pdf_url": "https://example/source.pdf", "pdf_access": {"sha256": "sourcehash"}}
    target = {"paper_id": "targetv1", "work_id": "arxiv:1234.56789", "title": title,
              "authors": ["Alice Example"], "year": 2020}
    text, starts, ends = normalize(raw)
    page = {"raw_text": raw, "raw_sha256": digest(raw), "text": text, "raw_starts": starts, "raw_ends": ends}
    chunk = {"id": "citationchunk", "paper_id": "source", "page": 1, "start_char": 0,
             "end_char": len(text), "text": text}
    row = {"source_paper_id": "source", "target_work_id": target["work_id"],
           "selected_target_paper_id": "targetv1", "relation": "CITES", "evidence_id": "TEST-C",
           "source_pdf_url": source["pdf_url"], "source_pdf_sha256": "sourcehash", "pdf_page_1based": "1",
           "page_text_sha256": digest(raw), "title_start_char_0based": str(start),
           "title_end_char_exclusive": str(end), "target_version_as_cited": "unspecified",
           "reference_locator": "Reference [22]", "identity_resolution": "explicit arXiv ID"}
    return row, source, target, [page], [chunk]


def test_citation_independently_verified_with_work_direction(citation_case):
    claim = verify_citation(*citation_case)
    assert (claim["subject_id"], claim["object_id"]) == ("source", "targetv1")
    assert claim["target_work_id"] == "arxiv:1234.56789"
    assert claim["target_version_as_cited"] == "unspecified"
    assert claim["status"] == "EXTRACTED"
    assert claim["source_location_status"] == "SOURCE_LOCATED"
    assert claim["student_review_status"] == "pending"
    assert claim["origin"] == "BIBLIOGRAPHY_VALIDATOR"
    validate_claims(citation_case[-1], [], [claim])


@pytest.mark.parametrize("field,value", [
    ("page_text_sha256", "wrong"), ("source_pdf_sha256", "wrong"), ("target_work_id", "wrong"),
    ("title_start_char_0based", "-1"), ("pdf_page_1based", "9"),
    ("reference_locator", "Reference [23]"), ("target_version_as_cited", "v1"),
])
def test_citation_tampering_rejected(citation_case, field, value):
    citation_case[0][field] = value
    with pytest.raises(ValueError):
        verify_citation(*citation_case)


def test_author_identity_is_not_inferred_from_title_alone(citation_case):
    citation_case[2]["authors"] = ["Different Person"]
    with pytest.raises(ValueError, match="author missing"):
        verify_citation(*citation_case)


def test_successful_ollama_response_is_validated_and_audited(extraction_case):
    chunk, output, model = extraction_case
    payload = {"message": {"content": json.dumps(output)}, "done": True, "done_reason": "stop"}

    def respond(request):
        sent = json.loads(request.content)
        assert sent["format"] == ollama_schema()
        assert sent["options"]["num_predict"] == 400
        return httpx.Response(200, json=payload)

    with httpx.Client(base_url="http://test", transport=httpx.MockTransport(respond)) as client:
        result = extract_sample(client, chunk, model)
    assert result["status"] == "VALIDATED_UNREVIEWED"
    assert result["claims"][0]["status"] == "EXTRACTED"
    assert result["response"] == payload
    assert "maxLength" not in json.dumps(ollama_schema())


def test_ollama_timeout_is_preserved(extraction_case):
    def timeout(request):
        raise httpx.ReadTimeout("test deadline", request=request)

    chunk, _, model = extraction_case
    with httpx.Client(base_url="http://test", transport=httpx.MockTransport(timeout)) as client:
        result = extract_sample(client, chunk, model)
    assert result["status"] == "FAILED"
    assert result["error"] == "ReadTimeout"
    assert "claims" not in result


def test_no_reference_heading_rejects_in_body_title(citation_case):
    row, _, _, pages, _ = citation_case
    pages[0]["raw_text"] = pages[0]["raw_text"].replace("References", "Discussion")
    pages[0]["raw_sha256"] = digest(pages[0]["raw_text"])
    row["page_text_sha256"] = pages[0]["raw_sha256"]
    with pytest.raises(ValueError, match="reference-section"):
        verify_citation(*citation_case)


def test_abstract_sampling_preserves_full_chunk_quote_offsets(extraction_case):
    chunk, output, model = extraction_case
    original = chunk["text"]
    prefix = "Title Authors Abstract"
    chunk["text"] = prefix + original

    def respond(request):
        messages = json.loads(request.content)["messages"]
        assert json.loads(messages[1]["content"])["passage"] == original
        return httpx.Response(200, json={"message": {"content": json.dumps(output)}, "done": True})

    with httpx.Client(base_url="http://test", transport=httpx.MockTransport(respond)) as client:
        result = extract_sample(client, chunk, model)
    assert result["status"] == "VALIDATED_UNREVIEWED"
    assert result["input_start_char"] == len(prefix)
    assert result["claims"][0]["start_char"] == len(prefix)


def test_author_date_citation_resolves_work_without_claiming_target_version(citation_case):
    row, source, target, _, _ = citation_case
    raw = "References\nExample, A. (2020). A Test Retrieval Method. Proceedings of Fictional Tests.\n"
    text, starts, ends = normalize(raw)
    row.update(reference_locator="References: Alice Example (2020)",
               identity_resolution="matching title/authors; published-work reference",
               page_text_sha256=digest(raw), title_start_char_0based=str(raw.index(target["title"])),
               title_end_char_exclusive=str(raw.index(target["title"]) + len(target["title"])))
    pages = [{"raw_text": raw, "raw_sha256": digest(raw), "text": text,
              "raw_starts": starts, "raw_ends": ends}]
    chunks = [{"id": "test", "paper_id": source["paper_id"], "page": 1,
               "start_char": 0, "end_char": len(text), "text": text}]
    result = verify_citation(row, source, target, pages, chunks)
    assert result["target_version_as_cited"] == "unspecified"
    assert result["status"] == "EXTRACTED"


def test_dpr_method_with_addresses_predicate_is_not_silently_repaired(extraction_case):
    chunk, output, model = extraction_case
    output["relations"][0]["predicate"] = "ADDRESSES"
    with pytest.raises(ValueError, match="predicate range"):
        validate_extraction(json.dumps(output), chunk, model)


def test_graphrag_repaired_hyphenation_is_not_fabricated_as_exact_quote(extraction_case):
    chunk, output, model = extraction_case
    chunk["text"] = "Our paper uses Widget on an in- dexed corpus."
    output["relations"][0]["quote"] = "Our paper uses Widget on an indexed corpus."
    with pytest.raises(ValueError, match="Supporting quote"):
        validate_extraction(json.dumps(output), chunk, model)
    output["relations"][0]["quote"] = "uses Widget on an in- dexed corpus"
    _, claims = validate_extraction(json.dumps(output), chunk, model)
    claim = claims[0]
    assert chunk["text"][claim["start_char"]:claim["end_char"]] == claim["quote"]
    assert claim["status"] == "EXTRACTED"


@pytest.mark.parametrize("core_failure,optional_failure,strict,expected", [
    (False, False, False, 0), (False, True, False, 0), (False, True, True, 2),
    (True, False, False, 1), (True, True, True, 1),
])
def test_import_and_optional_extraction_exit_contract(core_failure, optional_failure, strict, expected):
    from scripts.ingest import exit_code, finish_status
    report = {"failures": [{"error": "core"}] if core_failure else [],
              "import_status": "FAILED" if core_failure else "SUCCEEDED",
              "extractions": [{"status": "FAILED" if optional_failure else "VALIDATED_UNREVIEWED"}]}
    finish_status(report)
    assert exit_code(report, strict) == expected
    if optional_failure and not core_failure:
        assert report["import_status"] == "SUCCEEDED"
        assert report["overall_status"] == "PARTIAL_SUCCESS"


def test_method_samples_keep_original_chunk_coordinates():
    from scripts.ingest import select_samples
    chunk = {"id": "fixture", "page": 4, "text": "Context. In our pipeline, we use Leiden for communities."}
    sample = select_samples({"short_name": "GraphRAG"}, [chunk], 1)[0]
    assert sample["id"] == chunk["id"] and sample["text"] == chunk["text"]
    assert "Leiden" in sample["text"][sample["sample_start_char"]:sample["sample_end_char"]]


def test_method_schema_has_one_target_and_preserves_quote_checks(extraction_case):
    chunk, _, model = extraction_case
    chunk.update(sample_start_char=0, sample_end_char=len(chunk["text"]))
    output = {"relations": [{"entity": {"name": "Widget", "kind": "Method"}, "predicate": "USES",
                             "quote": "paper uses Widget for question answering.", "qualifiers": ""}]}
    entities, claims = validate_extraction(json.dumps(output), chunk, model)
    assert claims[0]["object_id"] == entities[0]["id"]
    assert claims[0]["status"] == "EXTRACTED"
    output["relations"][0]["predicate"] = "ADDRESSES"
    with pytest.raises(ValueError):
        validate_extraction(json.dumps(output), chunk, model)
    output["relations"][0]["predicate"] = "USES"
    output["relations"][0]["quote"] = "This invented phrase mentions Widget."
    with pytest.raises(ValueError, match="Supporting quote"):
        validate_extraction(json.dumps(output), chunk, model)
