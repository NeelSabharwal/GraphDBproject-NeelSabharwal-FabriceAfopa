"""PDF verification and page-bounded chunks with reversible text coordinates."""

import hashlib
import json
import os
import re
import tempfile
import unicodedata
import warnings
from pathlib import Path

import httpx
import pypdf

PROTOTYPE_IDS = {"arxiv:2004.04906v1", "arxiv:2005.11401v1", "arxiv:2404.16130v1"}
PARSER = f"pypdf-{pypdf.__version__}"
CHUNKER = "page-1400chars-overlap200-v1"
MAX_PDF_BYTES = 20 * 1024 * 1024


def digest(value: str | bytes) -> str:
    """Hash exact bytes or UTF-8 text, without implicit normalization."""
    return hashlib.sha256(value.encode("utf-8") if isinstance(value, str) else value).hexdigest()


def stable_id(*parts: object) -> str:
    """Produce an unambiguous deterministic identifier."""
    return digest(json.dumps(parts, ensure_ascii=False, separators=(",", ":")))


def prototype_manifest(root: Path) -> list[dict]:
    """Restrict downloads to the three authorized pinned arXiv sources."""
    data = json.loads((root / "corpus/corpus_manifest.json").read_text())
    papers = [paper for paper in data["papers"] if paper["selection_stage"] == "prototype"]
    if len(papers) != 3 or {p["paper_id"] for p in papers} != PROTOTYPE_IDS:
        raise ValueError("Manifest must contain exactly the three authorized prototype versions")
    for paper in papers:
        arxiv_id = paper["paper_id"].removeprefix("arxiv:")
        if paper["pdf_url"] != f"https://arxiv.org/pdf/{arxiv_id}":
            raise ValueError("Unexpected pinned PDF URL")
        if paper["suggested_download_path"] != f"data/raw/{arxiv_id}.pdf":
            raise ValueError("Unexpected PDF destination")
        if paper["paper_id"] != paper["work_id"] + paper["version"]:
            raise ValueError("Manifest work/version mismatch")
    return sorted(papers, key=lambda item: item["ingestion_priority"])


def verify_pdf(data: bytes, paper: dict) -> None:
    """Fail closed on wrong file type, size or pinned checksum."""
    if not data.startswith(b"%PDF-") or len(data) > MAX_PDF_BYTES:
        raise ValueError("Expected a PDF no larger than 20 MiB")
    if digest(data) != paper["pdf_access"]["sha256"]:
        raise ValueError(f"PDF checksum mismatch for {paper['paper_id']}; no alternate version accepted")
    if len(data) != paper["pdf_access"]["size_bytes"]:
        raise ValueError("PDF byte count differs from manifest")


def download_pdf(root: Path, paper: dict, client: httpx.Client) -> Path:
    """Reuse verified files; atomically save new downloads, never replace existing PDFs."""
    path = root / paper["suggested_download_path"]
    if path.exists():
        verify_pdf(path.read_bytes(), paper)
        return path
    with client.stream("GET", paper["pdf_url"]) as response:
        response.raise_for_status()
        if response.headers.get("content-type", "").split(";")[0] != "application/pdf":
            raise ValueError("Download did not return application/pdf")
        parts, total = [], 0
        for block in response.iter_bytes():
            total += len(block)
            if total > MAX_PDF_BYTES:
                raise ValueError("PDF download exceeds 20 MiB")
            parts.append(block)
    data = b"".join(parts)
    verify_pdf(data, paper)
    save_pdf(path, data, paper)
    return path


def save_pdf(path: Path, data: bytes, paper: dict) -> None:
    """Publish a complete verified file atomically; failures preserve the destination."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp",
                                         delete=False) as output:
            temporary = Path(output.name)
            output.write(data)
            output.flush()
            os.fsync(output.fileno())
        verify_pdf(temporary.read_bytes(), paper)
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def normalize(raw: str) -> tuple[str, list[int], list[int]]:
    """NFKC each character and collapse whitespace; map each output character to raw span.

    Offsets are Python characters, not PDF byte offsets or visual bounding boxes.
    Hyphenation is deliberately retained. Expanded ligatures map to the same raw character.
    """
    chars, starts, ends = [], [], []
    for index, char in enumerate(raw):
        for expanded in unicodedata.normalize("NFKC", char):
            normalized = " " if expanded.isspace() or unicodedata.category(expanded) == "Cc" else expanded
            if normalized == " " and chars and chars[-1] == " ":
                ends[-1] = index + 1
            else:
                chars.append(normalized)
                starts.append(index)
                ends.append(index + 1)
    return "".join(chars), starts, ends


def parse_pdf(path: Path, paper: dict) -> tuple[list[dict], list[dict]]:
    """Extract every PDF page, retaining failures and quality warnings for review."""
    verify_pdf(path.read_bytes(), paper)
    reader = pypdf.PdfReader(path)
    if len(reader.pages) != paper["pdf_access"]["page_count"]:
        raise ValueError("PDF page count differs from manifest")
    pages, problems = [], []
    for number, page in enumerate(reader.pages, 1):
        try:
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                raw = page.extract_text() or ""
            for warning in caught:
                problems.append({"page": number, "kind": "parser_warning", "detail": str(warning.message)})
        except Exception as error:  # Preserve the failed page and continue, never hide data loss.
            problems.append({"page": number, "kind": "parse_error", "detail": type(error).__name__})
            raw = ""
        if not raw.strip():
            problems.append({"page": number, "kind": "empty_page"})
        if any(unicodedata.category(char) == "Cc" and not char.isspace() for char in raw):
            problems.append({"page": number, "kind": "control_characters"})
        text, starts, ends = normalize(raw)
        pages.append({
            "page": number, "page_label": reader.page_labels[number - 1],
            "raw_text": raw, "raw_sha256": digest(raw), "text": text,
            "text_sha256": digest(text), "raw_starts": starts, "raw_ends": ends,
        })
    marker = paper["paper_id"].removeprefix("arxiv:")
    if not re.search(r"arXiv:\s*" + re.escape(marker) + r"(?!\d)", "".join(p["raw_text"] for p in pages)):
        raise ValueError(f"Expected arXiv identity/version marker not found: {marker}")
    return pages, problems


def make_chunks(paper: dict, pages: list[dict]) -> list[dict]:
    """Use 1400-character windows/200 overlap, bounded to pages and word boundaries."""
    chunks = []
    for page in pages:
        text, start = page["text"], 0
        while start < len(text):
            end = min(start + 1400, len(text))
            if end < len(text):
                boundary = text.rfind(" ", start + 1000, end)
                if boundary >= 0:
                    end = boundary + 1
            body = text[start:end]
            if body.strip():
                chunks.append({
                    "id": stable_id(paper["paper_id"], paper["pdf_access"]["sha256"],
                                    PARSER, CHUNKER, page["page"], start, end, digest(body)),
                    "paper_id": paper["paper_id"], "pdf_sha256": paper["pdf_access"]["sha256"],
                    "page": page["page"], "page_label": page["page_label"], "ordinal": len(chunks),
                    "start_char": start, "end_char": end, "text": body, "text_sha256": digest(body),
                    "raw_start_char": page["raw_starts"][start], "raw_end_char": page["raw_ends"][end - 1],
                    "page_raw_sha256": page["raw_sha256"], "parser_version": PARSER, "chunker_version": CHUNKER,
                })
            if end == len(text):
                break
            start = end - 200
            boundary = text.find(" ", start, end)
            if boundary >= 0:
                start = boundary + 1
    return chunks
