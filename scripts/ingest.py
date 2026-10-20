"""Import exactly the prototype manifest, with audit artifacts and bounded local extraction."""

import argparse
import csv
from datetime import datetime, timezone
import json
from pathlib import Path
import time
import uuid

import httpx
from neo4j import GraphDatabase

from app.config import Settings
from app.ingestion.citations import verify_citation
from app.ingestion.documents import digest, download_pdf, make_chunks, parse_pdf, prototype_manifest, stable_id
from app.ingestion.extraction import PROMPT_VERSION, extract_sample, validate_extraction
from app.ingestion.graph import EvidenceGraph


def save_json(path: Path, value: object) -> None:
    """Write generated audit data only under the explicitly selected artifact directory."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def select_samples(paper: dict, chunks: list[dict], count: int) -> list[dict]:
    """Bounded development samples from explicit method-use prose, not reference lists.

    Anchors locate source text, not gold model answers. Preserve full chunk coordinates.
    """
    if not count:
        return []
    anchors = {"DPR": (3, "in this work we use two independent"),
               "RAG": (3, "We use BART-large"),
               "GraphRAG": (4, "In our pipeline, we use Leiden")}
    page, anchor = anchors[paper["short_name"]]
    candidates = [c for c in chunks if c["page"] == page and anchor in c["text"]]
    if not candidates:
        raise ValueError(f"Method sampling anchor not found for {paper['short_name']}")
    chunk = min(candidates, key=lambda c: c["text"].index(anchor))
    start = max(0, chunk["text"].index(anchor) - 40)
    sample = {**chunk, "sample_start_char": start, "sample_end_char": min(len(chunk["text"]), start + 500)}
    others = [c for c in chunks if c["page"] == 1 and c["id"] != chunk["id"]]
    return [sample, *others[:count - 1]]


def finish_status(report: dict) -> None:
    """Publish separate machine-readable core-import and optional-extraction outcomes."""
    report["extraction_status"] = ("FAILED" if any(r["status"] == "FAILED" for r in report["extractions"])
                                   else "SUCCEEDED" if report["extractions"] else "NOT_REQUESTED")
    report["overall_status"] = ("FAILED" if report["failures"] else "PARTIAL_SUCCESS"
                                if report["extraction_status"] == "FAILED" else "SUCCEEDED")


def exit_code(report: dict, require_extraction: bool = False) -> int:
    """0: core succeeded; 1: core failure; 2: strict optional extraction failure."""
    if report["failures"]:
        return 1
    return 2 if require_extraction and report["extraction_status"] == "FAILED" else 0


def run(root: Path, sample_per_paper: int, download_only: bool = False) -> dict:
    """Verify all PDFs before graph mutations; retain partial failures and exact run timings."""
    started = time.perf_counter()
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8]
    artifact = root / "data/processed/ingestion" / run_id
    report = {"run_id": run_id, "started_at": datetime.now(timezone.utc).isoformat(),
              "papers": [], "failures": [], "extractions": [], "import_status": "NOT_STARTED"}
    try:
        papers = prototype_manifest(root)
        parsed = {}
        with httpx.Client(timeout=60, follow_redirects=True) as client:
            for paper in papers:
                path = download_pdf(root, paper, client)
                pages, problems = parse_pdf(path, paper)
                chunks = make_chunks(paper, pages)
                parsed[paper["paper_id"]] = (pages, chunks, problems)
                save_json(artifact / f"{paper['short_name']}-pages.json", pages)
                save_json(artifact / f"{paper['short_name']}-chunks.json", chunks)
                report["papers"].append({"id": paper["paper_id"], "sha256": digest(path.read_bytes()),
                                         "pages": len(pages), "chunks": len(chunks), "parse_problems": problems})
                print(f"Verified {paper['short_name']}: {len(pages)} pages, {len(chunks)} chunks", flush=True)
        if download_only:
            report["import_status"] = "NOT_REQUESTED"
            return report
        settings = Settings.from_environment()
        with (root / "corpus/citation_evidence.csv").open(newline="") as handle:
            citations = list(csv.DictReader(handle))
        report["manifest_sha256"] = digest((root / "corpus/corpus_manifest.json").read_bytes())
        report["citation_evidence_sha256"] = digest((root / "corpus/citation_evidence.csv").read_bytes())
        by_work = {paper["work_id"]: paper for paper in papers}
        with GraphDatabase.driver(
            settings.neo4j_uri, auth=(settings.neo4j_user, settings.neo4j_password.get_secret_value()),
            connection_timeout=5, max_transaction_retry_time=0,
        ) as driver, httpx.Client(base_url=settings.ollama_url, timeout=90, trust_env=False) as ollama:
            driver.verify_connectivity()
            graph = EvidenceGraph(driver)
            graph.ensure_schema()
            graph.register_papers(papers)
            paper_ids = [p["paper_id"] for p in papers]
            report["before_fingerprint"] = graph.fingerprint(paper_ids)
            model = None
            if sample_per_paper:
                try:
                    tags = ollama.get("/api/tags")
                    tags.raise_for_status()
                    model = next(m for m in tags.json()["models"] if m["name"] == settings.chat_model)
                    lock = json.loads((root / "models.lock.json").read_text())
                    expected = next(m for m in lock["models"] if m["name"] == settings.chat_model)
                    if model["digest"] != expected["digest"]:
                        raise ValueError("Installed extraction model digest differs from models.lock.json")
                    model = {"name": model["name"], "digest": model["digest"]}
                except (httpx.HTTPError, ValueError, KeyError, TypeError, StopIteration) as error:
                    report["extractions"].append({"status": "FAILED", "stage": "model_availability",
                                                   "error": type(error).__name__, "detail": str(error)[:500]})
                    model = None
            for paper in papers:
                pages, chunks, problems = parsed[paper["paper_id"]]
                entities, claims = [], []
                for row in citations:
                    if row["source_paper_id"] != paper["paper_id"] or row["target_work_id"] not in by_work:
                        continue
                    try:
                        claim = verify_citation(row, paper, by_work[row["target_work_id"]], pages, chunks)
                        claim["location_verified_at"] = report["started_at"]
                        claim["run_id"] = run_id
                        claims.append(claim)
                    except ValueError as error:
                        report["failures"].append({"evidence_id": row["evidence_id"], "detail": str(error)})
                try:
                    samples = select_samples(paper, chunks, sample_per_paper) if model else []
                except ValueError as error:
                    report["extractions"].append({"status": "FAILED", "paper_id": paper["paper_id"],
                                                   "stage": "sample_selection", "detail": str(error)})
                    samples = []
                for chunk in samples:
                    cache = root / "data/processed/extraction-cache" / (
                        stable_id(chunk["id"], model["digest"], PROMPT_VERSION,
                                  chunk.get("sample_start_char"), chunk.get("sample_end_char")) + ".json"
                    )
                    try:
                        if cache.exists():
                            result = json.loads(cache.read_text())
                            # Revalidate successful cached raw output against the current source.
                            if result["status"] == "VALIDATED_UNREVIEWED":
                                result["entities"], result["claims"] = validate_extraction(
                                    result["response"]["message"]["content"], chunk, model)
                            result["cache_reused"] = True
                        else:
                            result = extract_sample(ollama, chunk, model)
                            result["run_id"] = run_id
                            save_json(cache, result)
                    except (ValueError, TypeError, KeyError) as error:
                        result = {"status": "FAILED", "stage": "cache_validation", "chunk_id": chunk["id"],
                                  "error": type(error).__name__, "detail": str(error)[:500],
                                  "wall_seconds": 0, "cache_file": cache.name}
                        result["run_id"] = run_id
                    for claim in result.get("claims", []):
                        claim["run_id"] = result["run_id"]
                    entities.extend(result.get("entities", []))
                    claims.extend(result.get("claims", []))
                    report["extractions"].append({k: v for k, v in result.items()
                                                   if k not in {"response", "entities", "claims"}})
                    save_json(artifact / f"extraction-{chunk['id']}.json", result)
                    print(f"Extraction {paper['short_name']}: {result['status']} "
                          f"({result['wall_seconds']} s; cached={result.get('cache_reused', False)})", flush=True)
                save_json(artifact / f"{paper['short_name']}-claims.json", claims)
                graph.import_paper(paper["paper_id"], chunks, entities, claims,
                                   "PARSED_WITH_WARNINGS" if problems else "PARSED_NOT_VISUALLY_REVIEWED")
                next(p for p in report["papers"] if p["id"] == paper["paper_id"])["import_status"] = "SUCCEEDED"
            report["import_status"] = "SUCCEEDED"
            report["counts"] = graph.counts(paper_ids)
            report["after_fingerprint"] = graph.fingerprint(paper_ids)
            report["graph_unchanged"] = report["before_fingerprint"] == report["after_fingerprint"]
    except Exception as error:  # Save evidence on dependency/parse/import failure; caller exits nonzero.
        report["import_status"] = "FAILED"
        report["failures"].append({"error": type(error).__name__, "detail": str(error)[:1500]})
    finally:
        finish_status(report)
        report["wall_seconds"] = round(time.perf_counter() - started, 3)
        save_json(artifact / "report.json", report)
        print(json.dumps(report, indent=2), flush=True)
        print(f"Audit report: {artifact / 'report.json'}", flush=True)
    return report


def main() -> None:
    """CLI entry point; local operator access only, no unauthenticated HTTP import route."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("/workspace"))
    parser.add_argument("--sample-per-paper", type=int, choices=range(0, 3), default=1)
    parser.add_argument("--download-only", action="store_true")
    parser.add_argument("--require-extraction", action="store_true",
                        help="Exit 2 if core import succeeds but an optional extraction fails")
    args = parser.parse_args()
    report = run(args.root.resolve(), args.sample_per_paper, args.download_only)
    raise SystemExit(exit_code(report, args.require_extraction))


if __name__ == "__main__":
    main()
