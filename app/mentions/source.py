"""Read and authenticate existing graph/PDF sources without reimporting evidence."""

import json

from neo4j import READ_ACCESS

from app.ingestion.documents import digest, make_chunks, parse_pdf, prototype_manifest
from app.ingestion.research import require
from app.ingestion.reviews import load_decisions
from app.mentions.matcher import generate, rules

PROPOSAL_SHA256 = "990e943eb5be101d27a5435738be49aaadcee9a82faeb7ada92c6eb22b42f0b0"
POLICY_SHA256 = "6966fc03fb1633c782edc999acb6d6481fc01d0e5100f1a3b72e81c035c2645f"
BASELINE_SHA256 = "a847ebb5017a08830c281a64afbdba68a278d208e88f499ac7bde54628594682"


def encoded(value):
    """Canonical JSON for graph snapshots, including Neo4j temporal values."""
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), default=str)


def read_state(tx):
    """Read complete bounded state; element identities make drift visible."""
    nodes = tx.run(
        "MATCH (n) RETURN elementId(n) AS identity, labels(n) AS labels, "
        "properties(n) AS properties ORDER BY identity"
    ).data()
    edges = tx.run(
        "MATCH (a)-[r]->(b) RETURN elementId(r) AS identity, elementId(a) AS source, "
        "elementId(b) AS target, type(r) AS type, properties(r) AS properties ORDER BY identity"
    ).data()
    require(len(nodes) <= 5000 and len(edges) <= 20000, "Snapshot budget exceeded")
    for node in nodes:
        node["labels"].sort()
    return {"nodes": nodes, "relationships": edges}


def snapshot(driver):
    """Use explicit read access and rollback; never writes graph or catalog."""
    with driver.session(default_access_mode=READ_ACCESS) as session:
        with session.begin_transaction(timeout=30) as tx:
            state = read_state(tx)
            tx.rollback()
    return state


def fingerprint(state):
    """Hash every node/edge identity, type and property in the snapshot."""
    return digest(encoded(state))


def prepare(root, state):
    """Reconstruct all frozen occurrences from actual graph and original PDFs."""
    require(
        digest((root / "corpus/mentions_policy_v4.json").read_bytes()) == POLICY_SHA256, "Frozen policy hash mismatch"
    )
    decisions = load_decisions(root)
    papers = prototype_manifest(root)
    nodes = state["nodes"]
    by_element = {n["identity"]: n["properties"]["id"] for n in nodes}
    chunks = {n["properties"]["id"]: n["properties"] for n in nodes if "Chunk" in n["labels"]}
    entities = {n["properties"]["id"]: n["properties"] for n in nodes if "Entity" in n["labels"]}
    paper_nodes = {n["properties"]["id"]: n["properties"] for n in nodes if "Paper" in n["labels"]}
    parents = {c: [] for c in chunks}
    for edge in state["relationships"]:
        if edge["type"] == "PART_OF":
            parents[by_element[edge["source"]]].append(by_element[edge["target"]])
    pages, rebuilt, warnings = {}, {}, {}
    for paper in papers:
        ident = paper["paper_id"]
        require(paper_nodes[ident]["pdf_sha256"] == paper["pdf_access"]["sha256"], "Paper hash mismatch")
        pages[ident], warnings[ident] = parse_pdf(root / paper["suggested_download_path"], paper)
        for chunk in make_chunks(paper, pages[ident]):
            require(chunk["id"] in chunks and parents[chunk["id"]] == [ident], "Invalid PART_OF")
            require(all(chunks[chunk["id"]].get(k) == v for k, v in chunk.items()), "Source Chunk changed")
            rebuilt[chunk["id"]] = chunk
    require(len(rebuilt) == len(chunks) == 153, "Unexpected corpus Chunk set")
    for alias_id, alias in decisions["aliases"].items():
        if alias["outcome"] == "ACCEPT":
            entity = entities[alias["canonical_id"]]
            require(
                entity["alias_decision_id"] == alias_id
                and entity["resolution_status"] == "STUDENT_APPROVED_SCOPED"
                and json.loads(entity["alias_review_json"]) == alias,
                "Canonical identity changed",
            )
    candidates = generate({"chunks": rebuilt, "entities": entities, "decisions": decisions, "pages": pages}, rules())
    proposed = [r for r in candidates if r["decision"] == "PROPOSED"]
    data = json.dumps(proposed, ensure_ascii=False, indent=2) + "\n"
    require(len(proposed) == 145 and digest(data) == PROPOSAL_SHA256, "Proposal differs from authorized v4 artifact")
    return proposed, {
        "chunks": len(rebuilt),
        "proposed": len(proposed),
        "rejected": len(candidates) - len(proposed),
        "proposal_sha256": digest(data),
        "policy_sha256": POLICY_SHA256,
        "parse_warnings": warnings,
    }
