#!/usr/bin/env python3
"""Read-only, version-pinned checks for evaluation_gold.json evidence coordinates.

Usage:
    python verify_evaluation_evidence.py --gold evaluation_gold.json --pdf-dir .

Requires pypdf==6.10.0. This script does not modify source files.
"""

import argparse
import hashlib
import json
from pathlib import Path
import sys

import pypdf

EXPECTED_PYPDF_VERSION = "6.10.0"


def sha256(data: bytes | str) -> str:
    """Hash PDF bytes or unnormalized UTF-8 extracted text."""
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def check_evidence(gold: dict, pdf_dir: Path) -> int:
    """Verify PDF identities and each registered quote/context coordinate."""
    sources = {record["paper_id"]: record for record in gold["sources"]}
    pages_by_paper: dict[str, list[str]] = {}
    bad_sources: set[str] = set()
    failures = 0

    for paper_id, source in sources.items():
        pdf_name = paper_id.removeprefix("arxiv:") + ".pdf"
        path = pdf_dir / pdf_name
        if not path.is_file():
            print(f"FAIL source {paper_id}: missing {path}")
            bad_sources.add(paper_id)
            continue
        pdf_bytes = path.read_bytes()
        if sha256(pdf_bytes) != source["pdf_sha256"]:
            print(f"FAIL source {paper_id}: PDF SHA-256 mismatch; offsets not checked")
            bad_sources.add(paper_id)
            continue
        try:
            reader = pypdf.PdfReader(path)
            if len(reader.pages) != source["pdf_page_count"]:
                print(f"FAIL source {paper_id}: PDF page-count mismatch; offsets not checked")
                bad_sources.add(paper_id)
                continue
            pages_by_paper[paper_id] = [page.extract_text() or "" for page in reader.pages]
        except Exception as exc:
            print(f"FAIL source {paper_id}: PDF extraction error {type(exc).__name__}: {exc}")
            bad_sources.add(paper_id)
            continue
        print(f"OK   source {paper_id}: PDF hash and {len(reader.pages)} pages")

    evidence_ids = [record["evidence_id"] for record in gold["evidence"]]
    if len(evidence_ids) != len(set(evidence_ids)):
        print("FAIL evidence registry: duplicate evidence IDs")
        failures += 1
    all_ids = set(evidence_ids)
    for question in gold["questions"]:
        missing = set(question.get("evidence_ids", [])) - all_ids
        if missing:
            print(f"FAIL question {question['id']}: missing evidence IDs {sorted(missing)}")
            failures += 1

    checked = 0
    for evidence in gold["evidence"]:
        ident = evidence["evidence_id"]
        paper_id = evidence["paper_id"]
        if paper_id in bad_sources or paper_id not in pages_by_paper:
            print(f"SKIP {ident}: source PDF unavailable or failed identity checks")
            failures += 1
            continue
        page_number = evidence["pdf_page_1based"]
        pages = pages_by_paper[paper_id]
        if not isinstance(page_number, int) or not (1 <= page_number <= len(pages)):
            print(f"FAIL {ident}: PDF page {page_number} is out of bounds")
            failures += 1
            continue
        raw = pages[page_number - 1]
        if sha256(raw) != evidence["page_text_sha256"]:
            print(f"FAIL {ident}: page extracted-text SHA-256 mismatch; SKIPPING offsets")
            failures += 1
            continue

        start = evidence["excerpt_start_char_0based"]
        end = evidence["excerpt_end_char_exclusive"]
        context_start = evidence["context_start_char_0based"]
        context_end = evidence["context_end_char_exclusive"]
        if not (0 <= context_start <= start < end <= context_end <= len(raw)):
            print(f"FAIL {ident}: excerpt/context offsets invalid or outside page")
            failures += 1
            continue
        if raw[start:end] != evidence["supporting_excerpt"]:
            print(f"FAIL {ident}: excerpt differs at recorded character offsets")
            failures += 1
            continue
        if sha256(raw[context_start:context_end]) != evidence["context_text_sha256"]:
            print(f"FAIL {ident}: context extracted-text SHA-256 mismatch")
            failures += 1
            continue
        checked += 1
        print(f"PASS {ident}: page, excerpt offsets and context SHA-256")

    expected = len(gold["evidence"])
    print(f"\nEvidence checks: {checked}/{expected} passed; other errors: {failures}")
    if checked != expected or failures:
        print("RESULT: FAILED / NOT READY for offset-based grading")
        return 1
    print("RESULT: evidence registry coordinate/hash checks passed; semantic review and application testing STILL PENDING")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gold", type=Path, required=True, help="Path to unchanged evaluation_gold.json")
    parser.add_argument("--pdf-dir", type=Path, required=True, help="Folder containing the three pinned v1 PDF files")
    args = parser.parse_args()
    if pypdf.__version__ != EXPECTED_PYPDF_VERSION:
        print(f"STOP: installed pypdf {pypdf.__version__}; required {EXPECTED_PYPDF_VERSION} for reproducible offsets.", file=sys.stderr)
        return 2
    try:
        gold = json.loads(args.gold.read_text(encoding="utf-8"))
        return check_evidence(gold, args.pdf_dir)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"STOP: invalid/missing evaluation input ({type(exc).__name__}: {exc})", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
