"""Validate complete multi-chunk evidence before review and subsequent traversal."""

import json

from app.ingestion.documents import digest
from app.ingestion.research import require


def validate_bundle(claim, supports, chunks):
    """Reject missing, extra, corrupt or noncontiguous parts of a recorded bundle."""
    expected = json.loads(claim["support_manifest_json"])
    key = lambda s: (s["role"], s["part"])
    require(0 < len(expected) <= 8 and len(supports) == len(expected), "Incomplete source support bundle")
    require(sorted(supports, key=key) == sorted(expected, key=key), "Stored support differs from manifest")
    for support in supports:
        chunk = chunks[support["chunk_id"]]
        a, b = support["start_char"], support["end_char"]
        require(
            chunk["paper_id"] == claim["paper_id"] == claim["subject_id"]
            and chunk["pdf_sha256"] == claim["source_pdf_sha256"]
            and chunk["page_raw_sha256"] == claim["page_raw_sha256"]
            and chunk["page"] == claim["page"],
            "Incorrect supporting paper/page/PDF association",
        )
        require(digest(chunk["text"]) == chunk["text_sha256"], "Supporting chunk hash mismatch")
        require(type(a) is int and type(b) is int and 0 <= a < b <= len(chunk["text"]), "Invalid support offsets")
        require(
            chunk["text"][a:b] == support["quote"] and digest(support["quote"]) == support["quote_sha256"],
            "Supporting quote/hash mismatch",
        )
        require(
            (chunk["start_char"] + a, chunk["start_char"] + b) == (support["page_start"], support["page_end"]),
            "Support page offsets mismatch",
        )
    for role in ("excerpt", "context"):
        parts = sorted((s for s in supports if s["role"] == role), key=lambda s: s["part"])
        require(parts and [s["part"] for s in parts] == list(range(len(parts))), "Missing support part")
        require(all(a["page_end"] == b["page_start"] for a, b in zip(parts, parts[1:])), "Noncontiguous source context")
        text = "".join(s["quote"] for s in parts)
        require(
            text == claim[role + "_text"] and digest(text) == claim[role + "_text_sha256"],
            "Incomplete excerpt/context reconstruction",
        )


def stored_support(tx, claim_id):
    """Fetch all parts and authenticate their parent Paper; no status mutation."""
    record = tx.run("MATCH (c:Claim {id:$id}) RETURN properties(c) AS claim", id=claim_id).single(strict=True)
    claim = record["claim"]
    rows = list(
        tx.run(
            "MATCH (:Claim {id:$id})-[s:SUPPORTED_BY]->(chunk:Chunk) "
            "OPTIONAL MATCH (chunk)-[:PART_OF]->(p:Paper) "
            "RETURN properties(s) AS support,properties(chunk) AS chunk,p.id AS parent, "
            "p.pdf_sha256 AS pdf",
            id=claim_id,
        )
    )
    require(rows, "Claim lacks source support")
    for row in rows:
        require(
            row["parent"] == claim["paper_id"] == row["chunk"]["paper_id"], "Incorrect supporting paper association"
        )
    if claim.get("support_manifest_json"):
        require(all(r["pdf"] == claim["source_pdf_sha256"] for r in rows), "Parent PDF hash mismatch")
        supports = [dict(r["support"], chunk_id=r["chunk"]["id"]) for r in rows]
        validate_bundle(claim, supports, {r["chunk"]["id"]: r["chunk"] for r in rows})
    else:
        require(len(rows) == 1, "Legacy claim requires exactly one support")
        row, a, b = rows[0], claim["start_char"], claim["end_char"]
        require(
            row["chunk"]["id"] == claim["chunk_id"]
            and 0 <= a < b <= len(row["chunk"]["text"])
            and row["chunk"]["text"][a:b] == claim["quote"]
            and digest(claim["quote"]) == claim["quote_sha256"]
            and digest(row["chunk"]["text"]) == row["chunk"]["text_sha256"],
            "Stored supporting quote/hash no longer matches source",
        )
        require(
            all(row["support"][k] == claim[k] for k in ("quote", "quote_sha256", "start_char", "end_char")),
            "Stored supporting relationship mismatch",
        )
    return claim
