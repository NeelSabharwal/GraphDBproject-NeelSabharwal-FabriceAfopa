"""Extractive candidates with conservative lexical filtering, not semantic verification."""

import re

from app.agent.models import Draft

STOP = set("a an the how what which does do is are was were and or of to in for with it "
           "its their they this that use uses using give tell me paper papers v1 from "
           "within on by as can we our has have be at into each".split())


def terms(text):
    """Small English morphology heuristic; deliberately not an entailment classifier."""
    words = set()
    for word in re.findall(r"[a-z]{3,}", text.casefold()):
        if word in STOP:
            continue
        if word.endswith("ies"):
            word = word[:-3] + "y"
        for suffix in ("ation", "ion", "ing", "ers", "er", "ed", "es", "s", "e"):
            if word.endswith(suffix) and len(word) - len(suffix) >= 4:
                word = word[:-len(suffix)]
                break
        words.add(word)
    return words


def candidates(question, evidence):
    """Rank exact sentence spans; generic single-keyword matches are insufficient."""
    query = terms(question)
    found = []
    for cid, source in evidence.items():
        # Split only before a new capitalized sentence, avoiding most e.g./et al./equations.
        for raw in re.split(r"(?<=[.!?])\s+(?=[A-Z])", source["text"]):
            # Long sentences remain bounded contiguous spans, without text normalization.
            for start in range(0, len(raw), 550):
                quote = raw[start:start + 550].strip()
                overlap = query & terms(quote)
                if len(quote) < 25 or len(overlap) < 2:
                    continue
                found.append({"chunk_id": cid, "quote": quote, "score": len(overlap)})
    found.sort(key=lambda c: (-c["score"], len(c["quote"]), c["chunk_id"]))
    unique = []
    for row in found:
        if any(row["quote"] == old["quote"] for old in unique):
            continue
        unique.append(row)
    return [{"id": i, **row} for i, row in enumerate(unique[:12])]


def extractive_draft(selected, options, question):
    """Return only selected verbatim spans; omit duplicates and redundant query aspects."""
    by_id = {row["id"]: row for row in options}
    statements, covered, previous = [], set(), []
    query = terms(question)
    for index in selected:
        if index not in by_id:
            raise ValueError("Unknown source passage selection")
        row = by_id[index]
        words = terms(row["quote"])
        aspects = query & words
        if (not aspects - covered or any(
                len(words & old) / max(1, len(words | old)) >= 0.7 for old in previous)):
            continue
        statements.append({"text": row["quote"], "quote": row["quote"], "chunk_id": row["chunk_id"]})
        covered.update(aspects)
        previous.append(words)
    return Draft(statements=statements,
                 abstention="" if statements else "No sufficiently relevant source passage was selected.")
