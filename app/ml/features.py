"""Eight label-blind local graph features; no propagation between papers."""

import math

from app.analytics.service import accepted_entity
from app.ingestion.documents import digest
from app.ingestion.research import require
from app.mentions.graph import BATCH
from app.mentions.source import POLICY_SHA256

KINDS = ("Method", "Dataset", "Task", "Topic")
FEATURES = (
    "mentions_method_log1p",
    "mentions_dataset_log1p",
    "mentions_task_log1p",
    "mentions_topic_log1p",
    "jaccard_previous",
    "jaccard_next",
    "has_previous",
    "has_next",
)


def jaccard(left, right):
    """Empty neighborhoods overlap by zero, including two empty neighborhoods."""
    union = left | right
    return len(left & right) / len(union) if union else 0.0


def extract_features(state):
    """Use only authenticated canonical occurrence edges and same-paper NEXT."""
    by_element = {n["identity"]: n for n in state["nodes"]}
    chunks = {n["properties"]["id"]: n["properties"] for n in state["nodes"] if "Chunk" in n["labels"]}
    entities = {n["properties"]["id"]: n["properties"] for n in state["nodes"] if "Entity" in n["labels"]}
    mentions = {c: set() for c in chunks}
    previous = {c: set() for c in chunks}
    following = {c: set() for c in chunks}
    parents = {c: [] for c in chunks}
    for edge in state["relationships"]:
        source = by_element[edge["source"]]["properties"]
        target = by_element[edge["target"]]["properties"]
        a, b = source["id"], target["id"]
        if edge["type"] == "PART_OF" and a in chunks:
            require("Paper" in by_element[edge["target"]]["labels"], "Chunk parent is not Paper")
            parents[a].append(b)
            require(source["pdf_sha256"] == target["pdf_sha256"], "Parent PDF hash mismatch")
        elif edge["type"] == "NEXT" and (a in chunks or b in chunks):
            require(
                a in chunks and b in chunks and source["paper_id"] == target["paper_id"], "Invalid cross-paper NEXT"
            )
            following[a].add(b)
            previous[b].add(a)
        elif edge["type"] == "MENTIONS" and edge["properties"].get("batch_id") == BATCH:
            prop = edge["properties"]
            require(a in chunks and b in entities and accepted_entity(target), "Invalid canonical mention endpoint")
            require(
                prop.get("policy_sha256") == POLICY_SHA256 and prop.get("validation") == "EXACT_SURFACE",
                "Invalid controlled mention policy",
            )
            require(
                prop["text_sha256"] == source["text_sha256"]
                and source["text"][prop["start_char"] : prop["end_char"]] == prop["surface"],
                "Invalid mention source span",
            )
            require(target["kind"] in KINDS, "Unknown Entity kind")
            mentions[a].add(b)
    result = []
    for ident, chunk in sorted(chunks.items()):
        require(
            parents[ident] == [chunk["paper_id"]] and digest(chunk["text"]) == chunk["text_sha256"],
            "Invalid Chunk provenance",
        )
        require(len(previous[ident]) <= 1 and len(following[ident]) <= 1, "Ambiguous NEXT neighbors")
        left = next(iter(previous[ident]), None)
        right = next(iter(following[ident]), None)
        values = [math.log1p(sum(entities[e]["kind"] == kind for e in mentions[ident])) for kind in KINDS]
        values += [
            jaccard(mentions[ident], mentions[left]) if left else 0.0,
            jaccard(mentions[ident], mentions[right]) if right else 0.0,
            int(left is not None),
            int(right is not None),
        ]
        result.append(
            {
                "chunk_id": ident,
                "paper_id": chunk["paper_id"],
                "text_sha256": chunk["text_sha256"],
                "pdf_sha256": chunk["pdf_sha256"],
                "features": dict(zip(FEATURES, values)),
            }
        )
    return result
