"""Bibliography source-location checks, separate from student semantic review."""

import re
import unicodedata

from app.ingestion.documents import digest, stable_id

POLICY = "automated-bibliography-v1"


def identity_text(value: str) -> str:
    """Compare titles/authors ignoring layout punctuation, whitespace and ligatures."""
    return "".join(c for c in unicodedata.normalize("NFKC", value).casefold() if c.isalnum())


def verify_citation(row: dict, source: dict, target: dict, pages: list[dict], chunks: list[dict]) -> dict:
    """Recheck pinned bytes/page, title span, nearby author and explicit ID if supplied.

    Successful checks establish source location, never human semantic approval or
    knowledge of the target version read. Keep IDs stable to retain earlier evidence.
    """
    if row["source_paper_id"] != source["paper_id"] or row["relation"] != "CITES":
        raise ValueError("Citation source or relation mismatch")
    if row["source_pdf_sha256"] != source["pdf_access"]["sha256"] or row["source_pdf_url"] != source["pdf_url"]:
        raise ValueError("Citation source PDF provenance mismatch")
    if row["target_work_id"] != target["work_id"] or row["selected_target_paper_id"] != target["paper_id"]:
        raise ValueError("Citation target work identity mismatch")
    if row["target_version_as_cited"] != "unspecified":
        raise ValueError("This policy only resolves work-level citations with unspecified version")
    page_number = int(row["pdf_page_1based"])
    if not 1 <= page_number <= len(pages):
        raise ValueError("Citation page out of bounds")
    page = pages[page_number - 1]
    if page["raw_sha256"] != row["page_text_sha256"]:
        raise ValueError("Citation page hash mismatch; offsets cannot be trusted")
    start, end = int(row["title_start_char_0based"]), int(row["title_end_char_exclusive"])
    raw = page["raw_text"]
    if not 0 <= start < end <= len(raw):
        raise ValueError("Citation title offsets out of bounds")
    if identity_text(raw[start:end]) != identity_text(target["title"]):
        raise ValueError("Reference title does not match target work")
    # Independently require bibliography context, not just an in-body title mention.
    preceding = "\n".join(p["raw_text"] for p in pages[:page_number - 1]) + raw[:start]
    if not re.search(r"(?im)^\s*(?:\d+\s+)?references\s*$", preceding):
        raise ValueError("No reference-section heading precedes citation")
    before = raw[max(0, start - 400):start]
    after = raw[end:min(len(raw), end + 240)]
    surname = target["authors"][0].split()[-1]
    if identity_text(surname) not in identity_text(before):
        raise ValueError("Target first author missing from reference context")
    if row["reference_locator"].startswith("Reference ["):
        number = re.fullmatch(r"Reference \[(\d+)\]", row["reference_locator"])
        markers = re.findall(r"\[(\d+)\]", before)
        if number is None or not markers or markers[-1] != number[1]:
            raise ValueError("Numbered reference locator not found")
        before = before[before.rfind(f"[{number[1]}]"):]
    else:
        # The unnumbered prototype reference begins with the first author's surname.
        author_start = list(re.finditer(r"(?m)^" + re.escape(surname) + r",", before))
        if not author_start:
            raise ValueError("Author-date bibliography entry start not found")
        before = before[author_start[-1].start():]
        if str(target["year"]) not in before + after:
            raise ValueError("Reference year not found")
    if identity_text(surname) not in identity_text(before):
        raise ValueError("Target author is outside the located reference")
    if "explicit arXiv ID" in row["identity_resolution"]:
        if target["work_id"].removeprefix("arxiv:") not in before + after:
            raise ValueError("Explicit arXiv target ID not found in reference")
    normalized_start = next(i for i, raw_end in enumerate(page["raw_ends"]) if raw_end > start)
    normalized_end = max(i for i, raw_start in enumerate(page["raw_starts"]) if raw_start < end) + 1
    candidates = [c for c in chunks if c["page"] == page_number
                  and c["start_char"] <= normalized_start and c["end_char"] >= normalized_end]
    if not candidates:
        raise ValueError("No page-bounded chunk contains the reference title")
    chunk = candidates[0]
    quote = page["text"][normalized_start:normalized_end]
    local_start = normalized_start - chunk["start_char"]
    if chunk["text"][local_start:local_start + len(quote)] != quote:
        raise ValueError("Reference quote mapping failed")
    return {
        "id": stable_id(source["paper_id"], source["pdf_access"]["sha256"], row["evidence_id"], POLICY),
        "paper_id": source["paper_id"], "subject_id": source["paper_id"], "object_id": target["paper_id"],
        "predicate": "CITES", "status": "EXTRACTED", "origin": "BIBLIOGRAPHY_VALIDATOR",
        "source_location_status": "SOURCE_LOCATED", "location_policy": POLICY,
        "student_review_status": "pending", "evidence_id": row["evidence_id"],
        "target_work_id": target["work_id"], "target_version_as_cited": "unspecified",
        "reference_locator": row["reference_locator"], "source_pdf_sha256": source["pdf_access"]["sha256"],
        "source_url": source["pdf_url"], "page": page_number, "page_raw_sha256": page["raw_sha256"],
        "reference_raw_start": start, "reference_raw_end": end,
        "reference_context": before + raw[start:end] + after,
        "chunk_id": chunk["id"], "quote": quote, "quote_sha256": digest(quote),
        "start_char": local_start, "end_char": local_start + len(quote),
        "validation_checks": ["pdf_sha256", "page_sha256", "title_offsets", "target_title",
                              "reference_author", "reference_locator", "work_identity", "quote_mapping"],
    }
