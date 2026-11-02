"""Original synthetic sources/approvals; never apply real corpus review decisions."""

import asyncio
import csv
from copy import deepcopy
import json
import uuid

import pytest
from neo4j import GraphDatabase, AsyncGraphDatabase

from app.config import Settings
from app.ingestion.documents import digest, normalize, make_chunks
from app.ingestion.citations import verify_citation
from app.ingestion.graph import EvidenceGraph, refresh_citations
from app.ingestion.reviews import ALIAS_ENTITIES, REVIEW_PATH, resolve_alias, load_decisions
import app.ingestion.reviews as reviews
from app.ingestion.reviewed import ReviewedImporter, encoded, prepare
from app.ingestion.support import validate_bundle
from app.agent.tools import RetrievalTools
from scripts.integrate_reviewed_evidence import report, verify_applied, main


def page(raw, number):
    text, starts, ends = normalize(raw)
    return dict(
        page=number,
        page_label=str(number),
        raw_text=raw,
        raw_sha256=digest(raw),
        text=text,
        text_sha256=digest(text),
        raw_starts=starts,
        raw_ends=ends,
    )


@pytest.fixture
def research_fixture():
    """A full 22-assertion synthetic batch, with two pending bibliography records."""
    prefix = "test-reviewed-" + uuid.uuid4().hex
    papers = [
        dict(
            paper_id=prefix + s,
            work_id=prefix + s + "-work",
            version="v1",
            title="Original synthetic Paper " + s,
            authors=["Sample Tester"],
            year=2026,
            pdf_url="https://example.invalid/" + s,
            pdf_access={"sha256": digest(prefix + s)},
            reuse_note="Original synthetic test prose",
        )
        for s in ("a", "b", "c")
    ]
    raw = "Synthetic context. " * 60 + "Synthetic method evidence." + " Continued fixture context." * 50 + "\n"
    a = raw.index("Synthetic method evidence.")
    b, c, d = a + len("Synthetic method evidence."), 100, len(raw) - 100
    pages, chunks, citations = {}, {}, []
    for i, paper in enumerate(papers):
        target = papers[max(0, i - 1)]
        reference = "References\n[1] Sample Tester. " + target["title"] + ". 2026.\n"
        ident = paper["paper_id"]
        pages[ident] = [page(raw, 1), page(reference, 2)]
        chunks[ident] = make_chunks(paper, pages[ident])
        if i:
            start = reference.index(target["title"])
            citations.append(
                dict(
                    evidence_id="C03" if i == 1 else "C09",
                    source_paper_id=ident,
                    relation="CITES",
                    source_pdf_sha256=paper["pdf_access"]["sha256"],
                    source_pdf_url=paper["pdf_url"],
                    target_work_id=target["work_id"],
                    selected_target_paper_id=target["paper_id"],
                    target_version_as_cited="unspecified",
                    pdf_page_1based="2",
                    page_text_sha256=digest(reference),
                    title_start_char_0based=str(start),
                    title_end_char_exclusive=str(start + len(target["title"])),
                    reference_locator="Reference [1]",
                    identity_resolution="matching title and authors",
                )
            )
    aliases = {
        k: dict(
            canonical_id=prefix + "-" + v,
            outcome="ACCEPT",
            decision="APPROVED",
            reviewer="SYNTHETIC TEST STUDENT",
            accepted_scope="Synthetic bounded identity",
        )
        for k, v in ALIAS_ENTITIES.items()
    }
    for i in range(15, 22):
        aliases[f"A{i:02}"] = dict(
            canonical_id=None,
            outcome="NEEDS_CLARIFICATION" if i == 17 else "REJECT",
            decision="APPROVED",
            accepted_scope="Synthetic no merge",
        )
    decisions = dict(claims={}, aliases=aliases, inputs_sha256={REVIEW_PATH: "SYNTHETIC DOCUMENT HASH"})
    candidates = []
    for i, alias_index in enumerate([5, 6, 1, 2, 3, 4, 7, 5, 8, 6, 1, 2, 3, 4, 9, 10, 11, 12, 13, 14], 1):
        ident, alias = f"GE{i:02}", aliases[f"A{alias_index:02}"]
        paper = papers[0 if i <= 6 else 1 if i <= 14 else 2]
        kind = {"dataset": "Dataset", "method": "Method", "task": "Task"}[
            ALIAS_ENTITIES[f"A{alias_index:02}"].split(":")[0]
        ]
        row = dict(
            candidate_id=ident,
            source_paper_id=paper["paper_id"],
            subject_id=paper["paper_id"],
            subject_kind="Paper",
            object_proposed_id=alias["canonical_id"],
            object_kind=kind,
            predicate={"Dataset": "EVALUATED_ON", "Method": "USES", "Task": "ADDRESSES"}[kind],
            normalized_proposed_entity_name="Synthetic " + str(alias_index),
            object_surface_form="Synthetic",
            pdf_page_1based="1",
            page_text_sha256=digest(raw),
            supporting_excerpt=raw[a:b],
            excerpt_start_char_0based=str(a),
            excerpt_end_char_exclusive=str(b),
            context_start_char_0based=str(c),
            context_end_char_exclusive=str(d),
            context_text_sha256=digest(raw[c:d]),
            pdf_sha256=paper["pdf_access"]["sha256"],
            pdf_url=paper["pdf_url"] + "#page=1",
            parser="pypdf",
            parser_version="6.10.0",
            research_origin="SYNTHETIC_TEST",
            qualifier="Synthetic component only; no scientific finding",
            ambiguity="Synthetic scope only",
        )
        candidates.append(row)
        decisions["claims"][ident] = dict(
            decision="APPROVED",
            reviewer="SYNTHETIC TEST STUDENT",
            signoff_recorded_date="2026-01-01",
            accepted_scope="SYNTHETIC FIXTURE ONLY",
            inspected_sources="Synthetic pages",
            review_context=[["Synthetic qualifications"]],
            assertion={k: row[k] for k in ("source_paper_id", "predicate", "object_proposed_id", "object_kind")},
        )
    for row in citations:
        decisions["claims"][row["evidence_id"]] = dict(
            decision="APPROVED",
            reviewer="SYNTHETIC TEST STUDENT",
            signoff_recorded_date="2026-01-01",
            accepted_scope="Synthetic work-level citation only",
            inspected_sources="Synthetic bibliography",
            review_context=[["SYNTHETIC ONLY"]],
        )
    inputs = dict(papers=papers, pages=pages, candidates=candidates, citations=citations, decisions=decisions)
    nodes, edges = [], []
    for paper in papers:
        ident = paper["paper_id"]
        nodes.append(
            dict(
                id=ident,
                labels=["Paper"],
                properties=dict(
                    id=ident, work_id=paper["work_id"], pdf_sha256=paper["pdf_access"]["sha256"], source_version="v1"
                ),
            )
        )
        for chunk in chunks[ident]:
            nodes.append(dict(id=chunk["id"], labels=["Chunk"], properties=chunk))
            edges.append(dict(source=chunk["id"], type="PART_OF", target=ident, properties={}))
    return inputs, dict(nodes=nodes, edges=edges, fingerprint="synthetic"), chunks


@pytest.mark.parametrize(
    "field,value",
    [
        ("page_text_sha256", "wrong"),
        ("context_text_sha256", "wrong"),
        ("excerpt_start_char_0based", "0"),
        ("context_end_char_exclusive", "99999"),
        ("pdf_sha256", "wrong"),
        ("subject_id", "wrong"),
        ("predicate", "EVALUATED_ON"),
        ("object_kind", "Dataset"),
    ],
)
def test_preparation_rejects_source_and_assertion_mismatches(research_fixture, field, value):
    inputs, state, _ = research_fixture
    inputs["candidates"][0][field] = value
    with pytest.raises(ValueError):
        prepare(inputs, state)


@pytest.mark.parametrize("change", ["parent", "text", "hash", "page_hash", "version"])
def test_live_source_associations_are_authenticated(research_fixture, change):
    inputs, state, _ = research_fixture
    chunk = next(n["properties"] for n in state["nodes"] if "Chunk" in n["labels"])
    if change == "parent":
        state["edges"][0]["target"] = "wrong-paper"
    elif change == "version":
        state["nodes"][0]["properties"]["source_version"] = "v2"
    else:
        chunk[{"text": "text", "hash": "text_sha256", "page_hash": "page_raw_sha256"}[change]] = "wrong"
    with pytest.raises(ValueError):
        prepare(inputs, state)


@pytest.mark.parametrize("change", ["missing", "reject", "unresolved", "ambiguous"])
def test_missing_decisions_and_unapproved_aliases_fail(research_fixture, change):
    inputs, _, _ = research_fixture
    decisions = inputs["decisions"]
    row = inputs["candidates"][0]
    if change == "missing":
        del decisions["claims"]["GE01"]
    elif change == "ambiguous":
        decisions["aliases"]["A99"] = deepcopy(decisions["aliases"]["A05"])
    else:
        decisions["aliases"]["A05"]["outcome"] = "REJECT" if change == "reject" else "NEEDS_CLARIFICATION"
    with pytest.raises(ValueError):
        resolve_alias(decisions, row)


def test_complete_context_and_qualified_claims(research_fixture):
    inputs, state, _ = research_fixture
    plan = prepare(inputs, state)
    assert len(plan["claims"]) == 22 and len(plan["entities"]) == 14
    claim = next(c for c in plan["claims"] if c["evidence_id"] == "GE20")
    parts = plan["supports"][claim["id"]]
    assert len([s for s in parts if s["role"] == "context"]) >= 2
    assert claim["evaluation_stage"] == "entity_extraction" and claim["evaluation_scope"] == "COMPONENT_ONLY"
    assert claim["source_qualifier"] == inputs["candidates"][-1]["qualifier"]
    assert json.loads(claim["review_context_json"]) == inputs["decisions"]["claims"]["GE20"]["review_context"]
    by_id = {n["id"]: n["properties"] for n in state["nodes"] if "Chunk" in n["labels"]}
    with pytest.raises(ValueError, match="Incomplete"):
        validate_bundle(claim, parts[:-1], by_id)
    corrupted = deepcopy(parts)
    corrupted[0]["quote"] = "forged"
    with pytest.raises(ValueError):
        validate_bundle(claim, corrupted, by_id)
    assert all(c["status"] == "EXTRACTED" for c in plan["claims"])
    assert plan["aliases"]["A17"]["outcome"] == "NEEDS_CLARIFICATION"
    assert plan["aliases"]["A15"]["canonical_id"] is None


@pytest.mark.parametrize("change", ["reverse", "version"])
def test_work_level_citation_direction_and_revision(research_fixture, change):
    inputs, state, _ = research_fixture
    if change == "reverse":
        inputs["citations"][0]["source_paper_id"] = inputs["papers"][0]["paper_id"]
    else:
        inputs["citations"][0]["target_version_as_cited"] = "v1"
    with pytest.raises(ValueError):
        prepare(inputs, state)


def test_review_document_tampering_rejected(tmp_path):
    p = tmp_path / REVIEW_PATH
    p.parent.mkdir()
    p.write_text("Unsigned replacement")
    with pytest.raises(ValueError, match="Merged PR #5"):
        load_decisions(tmp_path)


def test_cli_requires_explicit_apply_fingerprint():
    with pytest.raises(SystemExit) as failure:
        main(["--apply"])
    assert failure.value.code == 2


@pytest.fixture
def signed_document_fixture(tmp_path, monkeypatch, research_fixture):
    """A toy document for parser tests; not a real signature or application input."""
    inputs, _, _ = research_fixture
    (tmp_path / "docs").mkdir()
    (tmp_path / "corpus").mkdir()
    for filename, rows in [
        ("GRAPH_EVIDENCE_CANDIDATES.csv", inputs["candidates"]),
        ("citation_evidence.csv", inputs["citations"]),
    ]:
        with (tmp_path / "corpus" / filename).open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    (tmp_path / "corpus/corpus_manifest.json").write_text("{}")
    lines = [
        "SYNTHETIC PARSER FIXTURE ONLY",
        "## 2. Context",
        "| GE20 | component only |",
        "## 6. Alias recommendations",
    ]
    for i in range(1, 22):
        outcome = "ACCEPT" if i <= 14 else "NEEDS_CLARIFICATION" if i == 17 else "REJECT"
        lines.append(f"| A{i:02} | synthetic mapping | {outcome} | synthetic boundary |")
    lines += ["## 7. Source checks", "## 9. Student sign-off: synthetic parser test"]
    for ident in inputs["decisions"]["claims"]:
        lines.append(f"| {ident} | RECOMMENDED | synthetic | APPROVED | fabrice12345C | 2026-10-21 | synthetic scope |")
    for i in range(1, 22):
        outcome = "ACCEPT" if i <= 14 else "NEEDS_CLARIFICATION" if i == 17 else "REJECT"
        lines.append(f"| A{i:02} | {outcome} | APPROVED | fabrice12345C | 2026-10-21 (recorded) | synthetic scope |")
    lines += ["## 10. End"]
    (tmp_path / REVIEW_PATH).write_text("\n".join(lines))
    snapshot = reviews.decision_snapshot(tmp_path)
    (tmp_path / reviews.DECISIONS_PATH).write_text(json.dumps(snapshot))
    # Only this parser fixture substitutes pins. The actual CLI has no override.
    monkeypatch.setattr(reviews, "REVIEW_SHA256", snapshot["inputs_sha256"][REVIEW_PATH])
    monkeypatch.setattr(reviews, "INPUT_HASHES", snapshot["inputs_sha256"])
    return tmp_path, snapshot


def test_transcribed_decisions_keep_rejections_and_unknown_inspection_time(signed_document_fixture):
    root, snapshot = signed_document_fixture
    assert load_decisions(root) == snapshot
    assert len(snapshot["claims"]) == 22 and len(snapshot["aliases"]) == 21
    assert snapshot["source_inspection_timestamp"] is None
    assert snapshot["aliases"]["A15"]["outcome"] == "REJECT"
    assert snapshot["aliases"]["A17"]["outcome"] == "NEEDS_CLARIFICATION"
    assert snapshot["aliases"]["A05"]["canonical_id"] == "method:bert-base"


@pytest.mark.parametrize("change", ["missing_decision", "widen_scope", "accept_rejected_alias", "change_input_hash"])
def test_derived_manifest_is_not_independent_authorization(signed_document_fixture, change):
    root, snapshot = signed_document_fixture
    if change == "missing_decision":
        del snapshot["claims"]["GE20"]
    elif change == "widen_scope":
        snapshot["claims"]["GE20"]["accepted_scope"] = "End-to-end accuracy"
    elif change == "accept_rejected_alias":
        snapshot["aliases"]["A16"]["outcome"] = "ACCEPT"
    else:
        snapshot["inputs_sha256"] = {**snapshot["inputs_sha256"], "extra": "wrong"}
    (root / reviews.DECISIONS_PATH).write_text(json.dumps(snapshot))
    with pytest.raises(ValueError):
        load_decisions(root)


@pytest.fixture
def live_research(research_fixture):
    inputs, _, chunks = research_fixture
    config = Settings.from_environment()
    with GraphDatabase.driver(
        config.neo4j_uri, auth=(config.neo4j_user, config.neo4j_password.get_secret_value())
    ) as driver:
        graph = EvidenceGraph(driver)
        ids = [p["paper_id"] for p in inputs["papers"]]
        entities = [a["canonical_id"] for a in inputs["decisions"]["aliases"].values() if a["canonical_id"]]
        try:
            graph.register_papers(inputs["papers"])
            for paper in inputs["papers"]:
                claims = []
                for row in inputs["citations"]:
                    if row["source_paper_id"] == paper["paper_id"]:
                        target = next(p for p in inputs["papers"] if p["paper_id"] == row["selected_target_paper_id"])
                        claims.append(
                            verify_citation(
                                row, paper, target, inputs["pages"][paper["paper_id"]], chunks[paper["paper_id"]]
                            )
                        )
                graph.import_paper(paper["paper_id"], chunks[paper["paper_id"]], [], claims, "SYNTHETIC")
            yield driver, ReviewedImporter(driver, inputs)
        finally:
            driver.execute_query(
                "MATCH (n) WHERE n.id IN $ids OR n.paper_id IN $papers DETACH DELETE n", ids=ids + entities, papers=ids
            )


@pytest.mark.integration
def test_atomic_application_and_repeat_run_preserve_history_and_exact_graph(live_research):
    driver, importer = live_research
    before, plan = importer.dry_run()
    assert report(before, plan)["actions"] == {"CREATE_AND_RECORD_APPROVAL": 20, "REUSE_PENDING_AND_RECORD_APPROVAL": 2}
    assert not any(e["type"] == "CITES" for e in before["edges"])
    assert importer.inspect()["fingerprint"] == before["fingerprint"]
    with pytest.raises(ValueError, match="not fully applied"):
        verify_applied(importer, before, plan)
    importer.apply(before["fingerprint"])  # Explicit SYNTHETIC operator action only.
    after, applied = importer.dry_run()
    assert {r["action"] for r in applied["changes"]} == {"REUSE_APPROVED"}
    verified = verify_applied(importer, after, applied)
    assert len(verified["scientific_assertions"]) == 20
    assert len(verified["shared_datasets"]) == 4
    assert EvidenceGraph(driver).counts(importer.paper_ids)["nodes"]["Entity"] == 14
    assert verified["actual_paths"][0]["papers"] == list(reversed(importer.paper_ids))
    for n in after["nodes"]:
        if "Claim" in n["labels"]:
            c = n["properties"]
            assert c["reviewer"] == "SYNTHETIC TEST STUDENT"
            assert c["signoff_recorded_date"] == "2026-01-01"
            assert c["review_applied_at"] == c["reviewed_at"]
            assert len(c["review_history"]) == 1
            if c["predicate"] == "CITES":
                assert c["target_version_as_cited"] == "unspecified"
                assert len(c["prior_evidence_history"]) == 1
    importer.apply(after["fingerprint"])
    assert importer.inspect()["fingerprint"] == after["fingerprint"]
    # Original ingestion may be repeated without replacing the enriched review/support.
    for row in importer.inputs["citations"]:
        source = next(p for p in importer.inputs["papers"] if p["paper_id"] == row["source_paper_id"])
        target = next(p for p in importer.inputs["papers"] if p["paper_id"] == row["selected_target_paper_id"])
        chunks = make_chunks(source, importer.inputs["pages"][source["paper_id"]])
        old_claim = verify_citation(row, source, target, importer.inputs["pages"][source["paper_id"]], chunks)
        EvidenceGraph(driver).import_paper(source["paper_id"], chunks, [], [old_claim], "SYNTHETIC")
    assert importer.inspect()["fingerprint"] == after["fingerprint"]

    # Actual retrieval validates every context part and retains scope downstream.
    async def retrieve():
        config = Settings.from_environment()
        async with AsyncGraphDatabase.driver(
            config.neo4j_uri, auth=(config.neo4j_user, config.neo4j_password.get_secret_value())
        ) as d:
            tools = RetrievalTools(d, None, config)
            result = await tools.execute(
                "find_citation_path", dict(source_id=importer.paper_ids[2], target_id=importer.paper_ids[0])
            )
            assert result["paths"][0]["papers"] == list(reversed(importer.paper_ids))
            assert all(
                c["target_version_as_cited"] == "unspecified"
                for edge in result["paths"][0]["edges"]
                for c in edge["claims"]
            )
            claim = next(c for c in applied["claims"] if c["evidence_id"] == "GE20")
            _, supports = await tools.claim_supports([claim["id"]])
            assert all(s["evaluation_scope"] == "COMPONENT_ONLY" for s in supports)
            expanded = await tools.execute("expand_verified_evidence", dict(paper_id=importer.paper_ids[0]))
            assert expanded["status"] == "ok"
            assert {c["subject_id"] for c in expanded["paths"][0]["claims"]} == set(importer.paper_ids[:2])
            assert all("source_qualifier" in c for c in expanded["paths"][0]["claims"])

    asyncio.run(retrieve())


@pytest.mark.integration
def test_failure_mid_review_rolls_back_every_added_node_and_edge(live_research, monkeypatch):
    _, importer = live_research
    before, _ = importer.dry_run()
    original = EvidenceGraph.review_claim
    count = 0

    def fail(graph, *args, **kwargs):
        nonlocal count
        count += 1
        original(graph, *args, **kwargs)
        if count == 2:
            raise ValueError("Synthetic interruption after two reviews")

    monkeypatch.setattr(EvidenceGraph, "review_claim", fail)
    with pytest.raises(ValueError, match="Synthetic interruption"):
        importer.apply(before["fingerprint"])
    assert importer.inspect()["fingerprint"] == before["fingerprint"]


@pytest.mark.integration
def test_existing_rejection_and_stale_fingerprint_cannot_be_overwritten(live_research):
    driver, importer = live_research
    before, plan = importer.dry_run()
    cid = next(c["id"] for c in plan["claims"] if c["predicate"] == "CITES")
    EvidenceGraph(driver).review_claim(cid, "SYNTHETIC TEST STUDENT", "Synthetic rejection", approved=False)
    rejected = importer.inspect()["fingerprint"]
    with pytest.raises(ValueError, match="Graph changed"):
        importer.apply(before["fingerprint"])
    with pytest.raises(ValueError, match="cannot be overwritten"):
        importer.dry_run()
    assert importer.inspect()["fingerprint"] == rejected


@pytest.mark.integration
def test_corrupt_approved_context_prevents_refresh_and_traversal(live_research):
    driver, importer = live_research
    before, plan = importer.dry_run()
    importer.apply(before["fingerprint"])
    claim = next(c for c in plan["claims"] if c["evidence_id"] == "C03")
    driver.execute_query(
        'MATCH (:Claim {id:$id})-[s:SUPPORTED_BY {role:"context"}]->() SET s.quote="forged"', id=claim["id"]
    )
    corrupted = importer.inspect()["fingerprint"]
    with driver.session() as session:
        with pytest.raises(ValueError):
            session.execute_write(refresh_citations, claim["paper_id"])
    assert importer.inspect()["fingerprint"] == corrupted
    with pytest.raises(ValueError):
        importer.dry_run()


@pytest.mark.integration
@pytest.mark.parametrize(
    "field,value",
    [("human_reviewed", False), ("student_review_status", "pending"), ("signoff_recorded_date", "1999-01-01")],
)
def test_verified_status_alone_cannot_make_import_verification_pass(live_research, field, value):
    driver, importer = live_research
    before, plan = importer.dry_run()
    importer.apply(before["fingerprint"])
    claim = plan["claims"][0]
    driver.execute_query("MATCH (c:Claim {id:$id}) SET c += $change", id=claim["id"], change={field: value})
    fingerprint = importer.inspect()["fingerprint"]
    with pytest.raises(ValueError, match="cannot be overwritten"):
        importer.dry_run()
    assert importer.inspect()["fingerprint"] == fingerprint
