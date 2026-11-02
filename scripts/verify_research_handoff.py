"""Offline research audit. Never send gold material to inference or graph writes."""

import argparse
from collections import Counter
import csv
import json
from pathlib import Path

from neo4j import GraphDatabase, Query
import pypdf

from app.config import Settings
from app.ingestion.documents import digest, parse_pdf, prototype_manifest
from app.ingestion.graph import EvidenceGraph
from app.ingestion.research import require, map_supports, verify_record


def check_structure(gold, rows, by_id):
    """Validate counts, references, review states and pinned source provenance."""
    errors = []

    def check(condition, detail):
        if not condition:
            errors.append(detail)

    check(len(rows) == 20, "Expected 20 scientific candidates")
    check(len({r["candidate_id"] for r in rows}) == len(rows), "Duplicate candidate IDs")
    check({r["candidate_id"] for r in rows} == {f"GE{i:02}" for i in range(1, 21)}, "Candidate IDs")
    check(len({r["object_proposed_id"] for r in rows}) == 14, "Expected 14 proposed entities")
    questions, evidence = gold["questions"], gold["evidence"]
    check(len(questions) == 15 and len({q["id"] for q in questions}) == 15, "Question IDs/count")
    check(len(evidence) == 20 and len({e["evidence_id"] for e in evidence}) == 20, "Evidence IDs/count")
    check(dict(Counter(q["gold_status"] for q in questions)) == gold["counts"], "Gold status counts")
    for question in questions:
        ident, review = question["id"], question["student_review"]
        check(set(question["evidence_ids"]) <= {e["evidence_id"] for e in evidence}, ident + ": references")
        check(
            review["status"] == "PENDING" and review["reviewer"] is None and review["reviewed_at"] is None,
            ident + ": unexpected student approval",
        )
    check(gold["results"] is None, "Gold unexpectedly contains executed results")
    check(gold["coordinate_convention"]["parser_version"] == "6.10.0", "Gold parser version")
    check({s["paper_id"] for s in gold["sources"]} == set(by_id), "Gold source set differs from prototype")
    for source in gold["sources"]:
        paper = by_id[source["paper_id"]]
        actual = tuple(source[k] for k in ("work_id", "version", "pdf_url", "pdf_sha256", "pdf_page_count"))
        expected = (
            paper["work_id"],
            paper["version"],
            paper["pdf_url"],
            paper["pdf_access"]["sha256"],
            paper["pdf_access"]["page_count"],
        )
        check(actual == expected, source["paper_id"] + ": source metadata differs from manifest")
    ranges = {"USES": {"Method"}, "EVALUATED_ON": {"Dataset"}, "ADDRESSES": {"Task", "Topic"}}
    for row in rows:
        ident, paper = row["candidate_id"], by_id.get(row["source_paper_id"])
        check(paper is not None, ident + ": unknown paper")
        if paper is None:
            continue
        check(row["subject_id"] == paper["paper_id"] and row["subject_kind"] == "Paper", ident + ": subject")
        check(row["object_kind"] in ranges.get(row["predicate"], set()), ident + ": predicate range")
        check(
            row["pdf_sha256"] == paper["pdf_access"]["sha256"]
            and row["pdf_url"] == paper["pdf_url"] + "#page=" + row["pdf_page_1based"],
            ident + ": PDF source",
        )
        check(row["parser"] == "pypdf" and row["parser_version"] == "6.10.0", ident + ": parser")
        check(
            (row["research_status"], row["proposed_import_claim_status"], row["student_review_status"])
            == ("SOURCE_LOCATED", "EXTRACTED", "PENDING"),
            ident + ": review states",
        )
        check(
            not any(row[k] for k in ("student_reviewer", "student_reviewed_at", "resolved_chunk_id")),
            ident + ": unexpected resolution/approval",
        )
        check(row["origin"] == "manual" and row["research_origin"] == "assistant_source_reading", ident + ": origin")
    for proposed in {r["object_proposed_id"] for r in rows}:
        definitions = {
            (r["object_kind"], r["normalized_proposed_entity_name"])
            for r in rows
            if r["object_proposed_id"] == proposed
        }
        check(len(definitions) == 1, proposed + ": inconsistent proposed entity definition")
    return errors


def audit(root):
    """Read PDFs and Neo4j through fixed queries; create no graph claims or approvals."""
    require(pypdf.__version__ == "6.10.0", "Requires pypdf 6.10.0")
    papers = prototype_manifest(root)
    by_id = {p["paper_id"]: p for p in papers}
    gold_path = root / "data/evaluation/evaluation_gold.json"
    csv_path = root / "corpus/GRAPH_EVIDENCE_CANDIDATES.csv"
    gold = json.loads(gold_path.read_text())
    with csv_path.open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    errors = check_structure(gold, rows, by_id)
    pages = {p["paper_id"]: parse_pdf(root / p["suggested_download_path"], p)[0] for p in papers}
    config = Settings.from_environment()
    with GraphDatabase.driver(
        config.neo4j_uri,
        auth=(config.neo4j_user, config.neo4j_password.get_secret_value()),
        connection_timeout=5,
        max_transaction_retry_time=0,
    ) as driver:
        graph = EvidenceGraph(driver)
        fingerprint = graph.fingerprint(list(by_id))
        with driver.session(default_access_mode="READ") as session:
            chunks = [
                dict(r)
                for r in session.run(
                    Query(
                        "MATCH (c:Chunk)-[:PART_OF]->(p:Paper) WHERE p.id IN $ids "
                        "RETURN p.id AS paper, c.id AS id, c.page AS page, c.start_char AS start, "
                        "c.end_char AS end, c.text_sha256 AS hash, c.text AS text",
                        timeout=10,
                    ),
                    ids=list(by_id),
                )
            ]
            citations = [
                dict(r)
                for r in session.run(
                    Query(
                        "MATCH (c:Claim) WHERE c.evidence_id IN ['C03','C09'] "
                        "RETURN c.id AS claim_id, c.evidence_id AS evidence_id, c.paper_id AS paper_id, "
                        "c.page AS page, c.status AS status, c.source_location_status AS location_status, "
                        "c.student_review_status AS review_status",
                        timeout=10,
                    )
                )
            ]
        for chunk in chunks:
            page = pages[chunk["paper"]][chunk["page"] - 1]
            if page["text"][chunk["start"] : chunk["end"]] != chunk["text"] or digest(chunk["text"]) != chunk["hash"]:
                errors.append(chunk["id"] + ": live chunk text/offset mismatch")
        mappings, passed = [], Counter()
        for kind, records in [("candidate", rows), ("gold_evidence", gold["evidence"])]:
            for record in records:
                ident = record["candidate_id"] if kind == "candidate" else record["evidence_id"]
                try:
                    mapping = verify_record(record, kind, pages, chunks)
                    mappings.append(mapping)
                    passed[kind] += 1
                except (ValueError, KeyError, IndexError, StopIteration) as error:
                    errors.append(ident + ": " + str(error))
        if graph.fingerprint(list(by_id)) != fingerprint:
            errors.append("Unexpected graph change during read-only audit")
        return {
            "parser": pypdf.__version__,
            "source_count": len(papers),
            "questions": len(gold["questions"]),
            "gold_status_counts": dict(Counter(q["gold_status"] for q in gold["questions"])),
            "candidate_count": len(rows),
            "proposed_entities": len({r["object_proposed_id"] for r in rows}),
            "candidate_predicates": dict(Counter(r["predicate"] for r in rows)),
            "verified_location_counts": dict(passed),
            "live_chunk_count": len(chunks),
            "graph_counts": graph.counts(list(by_id)),
            "citation_claims": citations,
            "graph_fingerprint": fingerprint,
            "errors": errors,
            "mappings": mappings,
            "q15_forged_output_fixture_present": "candidate_citation_to_validate"
            in gold["questions"][-1].get("test_fixture", {}),
            "inputs_sha256": {str(p.relative_to(root)): digest(p.read_bytes()) for p in (gold_path, csv_path)},
        }


def main():
    """Run this offline verifier explicitly; the application never loads gold through it."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, help="Local audit output; never written to graph")
    args = parser.parse_args()
    root = args.root.resolve()
    result = audit(root)
    out = args.output or root / "data/processed/research-review/validation.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "mappings"}, indent=2))
    print(
        "MAPPING_SUMMARY",
        [(m["id"], len(m["excerpt_supports"]), len(m["context_supports"])) for m in result["mappings"]],
    )
    return 1 if result["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
