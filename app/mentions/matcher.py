"""Frozen v4 matching semantics adapted from the inspected #8B audit.

No annotation files or model outputs are inputs. MENTIONS is never a Claim.
"""

import hashlib
import json
import re

from app.ingestion.research import require

VERSION = "scoped-exact-mentions-audit-v4"
DPR, RAG, GRAPH = "arxiv:2004.04906v1", "arxiv:2005.11401v1", "arxiv:2404.16130v1"


def rules():
    """Fixed before joining annotations; conservative subset of A01-A14."""
    result = []

    def add(alias, surfaces, mode="named", papers=None, expansion=None):
        for surface in surfaces:
            result.append({"alias": alias, "surface": surface, "mode": mode, "papers": papers, "expansion": expansion})

    add("A01", ["Natural Questions"])
    add("A01", ["NQ"], "definition", [DPR, RAG], ["Natural Questions"])
    add("A02", ["TriviaQA"])
    add("A02", ["Trivia"], "definition", [DPR], ["TriviaQA"])
    add("A02", ["TQA"], "definition", [RAG], ["TriviaQA"])
    add("A03", ["WebQuestions"])
    add("A03", ["WQ"], "definition", [DPR, RAG], ["WebQuestions"])
    add("A04", ["CuratedTREC", "CuratedTrec"])
    add("A04", ["TREC"], "definition", [DPR], ["CuratedTREC"])
    add("A04", ["CT"], "definition", [RAG], ["CuratedTrec"])
    add("A05", ["BERT-base", "BERT BASE", "base-uncased BERT"], papers=[DPR, RAG])
    add(
        "A06",
        [
            "open-domain question answering",
            "Open-domain question answering",
            "open-domain textual QA",
            "open-domain QA",
        ],
        papers=[DPR, RAG],
    )
    add("A07", ["DPR", "Dense Passage Retrieval"])
    add("A08", ["BART-large"])
    add("A09", ["Leiden"])
    add("A10", ["map-reduce approach", "map-reduce summarization", "Map-reduce summarization"], "workflow", [GRAPH])
    add("A11", ["query-focused summarization", "Query-focused summarization", "QFS"], papers=[GRAPH])
    add("A12", ["podcast transcripts", "Podcast transcripts", "Behind the Tech"], "corpus_context", [GRAPH])
    add("A13", ["news articles", "News articles", "MultiHop-RAG"], "corpus_context", [GRAPH])
    add("A14", ["HotPotQA", "HotpotQA"])
    # Diagnostic-only probes: never accepted identities or additional aliases.
    add("A05", ["BERT"], "ambiguous")
    add("A08", ["BART"], "ambiguous")
    add("A09", ["Louvain"], "rejected_equivalence")
    add("A10", ["Hadoop", "MapReduce"], "rejected_equivalence")
    add("A03", ["WebQuestionsSP"], "rejected_equivalence")
    add("A12", ["Podcast"], "ambiguous")
    add("A13", ["News"], "ambiguous")
    return result


def pattern(surface):
    # Scientific tokens/hyphenated variants are not substrings of approved names.
    return re.compile(r"(?<![\w-])" + re.escape(surface) + r"(?![\w-])")


def sha(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def section_reason(page, page_number, first_references, start, end):
    """Inspect original page lines through the unchanged reversible parser mapping."""
    raw_start, raw_end = page["raw_starts"][start], page["raw_ends"][end - 1]
    raw = page["raw_text"]
    if first_references and (page_number, raw_start) >= first_references:
        return "REFERENCE_OR_POST_REFERENCE_ZONE"
    if page_number == 1:
        body = re.search(r"(?m)^\s*Abstract\s*$", raw)
        if body and raw_end <= body.start():
            return "TITLE_OR_METADATA"
    # Deliberately conservative layout gate: the page prefix before its first
    # figure/table caption can mix labels, headers and table cells with prose.
    # Exclude the entire prefix rather than infer identity from that layout.
    caption = re.search(r"(?m)^(?:Figure|Table)\s+\d+\s*:", raw)
    if caption and raw_start < caption.start():
        return "PRE_CAPTION_REGION"
    line_start = raw.rfind("\n", 0, raw_start) + 1
    line_end = raw.find("\n", raw_end)
    line_end = len(raw) if line_end == -1 else line_end
    line = raw[line_start:line_end].strip()
    if re.sub(r"\s+", " ", line) == page["text"][start:end]:
        return "ISOLATED_LABEL"
    if len(line.split()) <= 2 and not re.search(r"[.!?;:]\s*$", line):
        return "SHORT_LABEL_OR_UNCERTAIN_WRAP"
    if (
        not re.search(r"[.!?;:]", line)
        and len(re.findall(r"\b(?:Question|Passage|Dataset|Train|Dev|Test)\b", line)) >= 2
    ):
        return "TABLE_COLUMN_HEADER"
    if len(line) <= 120 and re.match(r"^\d+(?:\.\d+)*\s+[A-Z]", line) and not re.search(r"[.!?]\s*$", line):
        return "NUMBERED_HEADING"
    if line in {"Abstract", "References", "Bibliography"}:
        return "HEADING"
    return None


def scope_reason(rule, paper, page, start, end):
    if rule["papers"] and paper not in rule["papers"]:
        return "OUTSIDE_APPROVED_PAPER_SCOPE"
    mode = rule["mode"]
    if mode in {"ambiguous", "rejected_equivalence"}:
        return mode.upper()
    text = page["text"]
    if mode == "definition":
        if not any(
            re.search(re.escape(expansion) + r"\s*\(\s*$", text[max(0, start - 80) : start])
            for expansion in rule["expansion"]
        ) or not re.match(r"\s*\)", text[end:]):
            return "SHORTHAND_NOT_EXPLICITLY_EXPANDED"
    if mode == "workflow" and page["page"] not in {3, 5}:
        return "OUTSIDE_REVIEWED_WORKFLOW_CONTEXT"
    if mode == "corpus_context":
        # Approved GraphRAG 3.1 corpus descriptions, not generic news/podcasts
        # or the original MultiHop-RAG QA benchmark/task elsewhere.
        left, right = text.find("3.1 Datasets"), text.find("3.2 Queries")
        if page["page"] != 6 or not 0 <= left <= start < end <= right:
            return "OUTSIDE_REVIEWED_CORPUS_DESCRIPTION"
    return None


def generate(snapshot, policy):
    entities, decisions = snapshot["entities"], snapshot["decisions"]["aliases"]
    references = {}
    for paper, pages in snapshot["pages"].items():
        refs = [
            (p["page"], m.start())
            for p in pages
            for m in re.finditer(r"(?m)^\s*(?:References|Bibliography)\s*$", p["raw_text"])
        ]
        require(bool(refs), "Missing reference boundary")
        references[paper] = min(refs)
    candidates = []
    for chunk in sorted(
        snapshot["chunks"].values(), key=lambda c: (c["paper_id"], c["page"], c["start_char"], c["id"])
    ):
        paper = chunk["paper_id"]
        page = snapshot["pages"][paper][chunk["page"] - 1]
        require(sha(chunk["text"]) == chunk["text_sha256"], "Chunk text/hash mismatch")
        for rule in policy:
            alias = decisions[rule["alias"]]
            entity = entities[alias["canonical_id"]]
            require(alias["outcome"] == "ACCEPT" and alias["decision"] == "APPROVED", "Unapproved alias")
            require(entity["alias_decision_id"] == rule["alias"], "Alias identity mismatch")
            for match in pattern(rule["surface"]).finditer(chunk["text"]):
                start, end = chunk["start_char"] + match.start(), chunk["start_char"] + match.end()
                reason = scope_reason(rule, paper, page, start, end)
                reason = section_reason(page, chunk["page"], references[paper], start, end) or reason
                record = {
                    "chunk_id": chunk["id"],
                    "paper_id": paper,
                    "entity_id": entity["id"],
                    "kind": entity["kind"],
                    "surface": match.group(),
                    "start_char": match.start(),
                    "end_char": match.end(),
                    "text_sha256": chunk["text_sha256"],
                    "pdf_sha256": chunk["pdf_sha256"],
                    "pdf_page_1based": chunk["page"],
                    "page_start_char": start,
                    "page_end_char": end,
                    "page_raw_sha256": page["raw_sha256"],
                    "raw_start_char": page["raw_starts"][start],
                    "raw_end_char": page["raw_ends"][end - 1],
                    "alias_id": rule["alias"],
                    "match_policy": VERSION,
                    "decision": "REJECTED" if reason else "PROPOSED",
                    "reason": reason,
                    "identity_scope": alias["boundary"],
                    "student_review_status": "NOT_REVIEWED",
                    "context": page["text"][max(0, start - 180) : end + 180],
                }
                key = [
                    record[k]
                    for k in ("chunk_id", "entity_id", "start_char", "end_char", "text_sha256", "match_policy")
                ]
                record["proposal_id"] = sha(json.dumps(key, separators=(",", ":")))
                candidates.append(record)
    # Suppress diagnostic subspans such as BERT in an accepted full BERT BASE match.
    accepted = [r for r in candidates if r["decision"] == "PROPOSED"]
    for r in candidates:
        if r["decision"] == "REJECTED" and any(
            a["chunk_id"] == r["chunk_id"]
            and a["entity_id"] == r["entity_id"]
            and a["start_char"] <= r["start_char"]
            and r["end_char"] <= a["end_char"]
            for a in accepted
        ):
            r["reason"] = "SUBSPAN_OF_ACCEPTED_NAME"
    require(len({r["proposal_id"] for r in candidates}) == len(candidates), "Duplicate candidate")
    return candidates
