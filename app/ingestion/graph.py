"""Parameterized evidence graph writes; one atomic transaction per paper."""

import json
from datetime import datetime, timezone

from neo4j import Query, unit_of_work

from app.ingestion.citations import POLICY
from app.ingestion.documents import CHUNKER, PARSER, digest

SCHEMA = (
    "CREATE CONSTRAINT paper_id IF NOT EXISTS FOR (n:Paper) REQUIRE n.id IS UNIQUE",
    "CREATE CONSTRAINT chunk_id IF NOT EXISTS FOR (n:Chunk) REQUIRE n.id IS UNIQUE",
    "CREATE CONSTRAINT entity_id IF NOT EXISTS FOR (n:Entity) REQUIRE n.id IS UNIQUE",
    "CREATE CONSTRAINT claim_id IF NOT EXISTS FOR (n:Claim) REQUIRE n.id IS UNIQUE",
    "CREATE INDEX paper_work IF NOT EXISTS FOR (n:Paper) ON (n.work_id)",
    "CREATE INDEX entity_lookup IF NOT EXISTS FOR (n:Entity) ON (n.kind, n.normalized_name)",
    "CREATE INDEX chunk_page IF NOT EXISTS FOR (n:Chunk) ON (n.paper_id, n.page)",
    "CREATE INDEX claim_review IF NOT EXISTS FOR (n:Claim) ON (n.status, n.predicate)",
)
HUMAN_POLICY = "student-semantic-review-v1"


def refresh_citations(tx, paper_id: str) -> None:
    """Derived edges require explicit human approval as well as verified status."""
    tx.run("MATCH (p:Paper {id:$id})-[r:CITES]->() DELETE r", id=paper_id).consume()
    tx.run(
        "MATCH (c:Claim {predicate:'CITES', status:'SOURCE_VERIFIED'})-[:SUBJECT]->(p:Paper {id:$id}), "
        "(c)-[:OBJECT]->(target:Paper), (c)-[:SUPPORTED_BY]->(:Chunk) "
        "WHERE c.human_reviewed=true AND c.student_review_status='approved' "
        "AND c.review_policy=$policy AND trim(coalesce(c.reviewer,''))<>'' AND c.reviewed_at IS NOT NULL "
        "WITH p, target, collect(DISTINCT c.id) AS claims "
        "MERGE (p)-[r:CITES]->(target) SET r.claim_ids=claims, r.target_work_id=target.work_id, "
        "r.target_version_as_cited='unspecified'", id=paper_id, policy=HUMAN_POLICY,
    ).consume()


def retain_pending_bibliography(tx, paper_id: str) -> None:
    """Correct only legacy automated approvals, retaining original metadata/history."""
    records = list(tx.run(
        "MATCH (c:Claim {paper_id:$id, predicate:'CITES', origin:'BIBLIOGRAPHY_VALIDATOR', "
        "status:'SOURCE_VERIFIED', review_policy:$policy}) WHERE coalesce(c.human_reviewed,false)=false "
        "RETURN properties(c) AS old", id=paper_id, policy=POLICY))
    for record in records:
        old = record["old"]
        event = json.dumps({"action": "restore_pending_student_review", "previous": old,
                            "at": datetime.now(timezone.utc).isoformat()}, sort_keys=True, default=str)
        tx.run(
            "MATCH (c:Claim {id:$id}) SET c.status='EXTRACTED', c.source_location_status='SOURCE_LOCATED', "
            "c.location_policy=$policy, c.location_verified_at=c.reviewed_at, c.human_reviewed=false, "
            "c.student_review_status='pending', c.review_history=coalesce(c.review_history,[])+[$event] "
            "REMOVE c.reviewer, c.reviewed_at, c.review_policy", id=old["id"], policy=POLICY, event=event,
        ).consume()


def validate_claims(chunks: list[dict], entities: list[dict], claims: list[dict]) -> None:
    """Validate provenance again at the graph write boundary, including cached data."""
    by_id = {chunk["id"]: chunk for chunk in chunks}
    entity_ids = {entity["id"] for entity in entities}
    for entity in entities:
        chunk = by_id.get(entity.get("chunk_id"))
        if chunk is None or entity["paper_id"] != chunk["paper_id"]:
            raise ValueError("Entity source chunk must exist in the batch and belong to the same paper")
    for claim in claims:
        chunk = by_id.get(claim["chunk_id"])
        if chunk is None or claim["paper_id"] != chunk["paper_id"] or claim["subject_id"] != chunk["paper_id"]:
            raise ValueError("Claim source must be its supporting chunk's paper")
        start, end = claim["start_char"], claim["end_char"]
        if not 0 <= start < end <= len(chunk["text"]):
            raise ValueError("Claim quote offsets out of bounds")
        if chunk["text"][start:end] != claim["quote"] or digest(claim["quote"]) != claim["quote_sha256"]:
            raise ValueError("Claim quote/hash does not match its supporting chunk")
        if claim["predicate"] == "CITES":
            if (claim["status"], claim["origin"], claim.get("location_policy"),
                claim.get("source_location_status")) != (
                "EXTRACTED", "BIBLIOGRAPHY_VALIDATOR", POLICY, "SOURCE_LOCATED"
            ):
                raise ValueError("Automatic citations must be source-located and pending human review")
        elif (claim["predicate"] not in {"USES", "EVALUATED_ON", "ADDRESSES"}
              or claim["status"] != "EXTRACTED" or claim["origin"] != "LLM"
              or claim["object_id"] not in entity_ids):
            raise ValueError("Automatic scientific claims must remain EXTRACTED with an existing entity")


class EvidenceGraph:
    """Keep schema, idempotency and transaction boundaries explicit for student review."""

    def __init__(self, driver):
        self.driver = driver

    def ensure_schema(self) -> None:
        """Create four identity constraints and workload-specific lookup indexes."""
        for statement in SCHEMA:
            self.driver.execute_query(Query(statement, timeout=30))

    def register_papers(self, papers: list[dict]) -> None:
        """Register verified metadata before cross-paper citation writes."""
        rows = [{
            "id": p["paper_id"], "work_id": p["work_id"], "title": p["title"], "authors": p["authors"],
            "year": p["year"], "source_url": p["pdf_url"], "source_version": p["version"],
            "pdf_sha256": p["pdf_access"]["sha256"], "license_note": p["reuse_note"],
            "parser_version": PARSER, "chunker_version": CHUNKER,
        } for p in papers]
        existing, _, _ = self.driver.execute_query(
            "UNWIND $rows AS row MATCH (p:Paper {id: row.id}) RETURN p.id AS id, "
            "p.pdf_sha256 AS hash, p.parser_version AS parser, p.chunker_version AS chunker", rows=rows,
        )
        by_id = {row["id"]: row for row in rows}
        for record in existing:
            row = by_id[record["id"]]
            if (record["hash"], record["parser"], record["chunker"]) != (
                row["pdf_sha256"], PARSER, CHUNKER
            ):
                raise ValueError("Existing paper has different PDF/parser/chunker; explicit migration required")
        self.driver.execute_query(
            "UNWIND $rows AS row MERGE (p:Paper {id: row.id}) "
            "ON CREATE SET p += row, p.parse_status = 'PENDING', p.created_at = datetime()", rows=rows,
        )

    def import_paper(self, paper_id: str, chunks: list[dict], entities: list[dict],
                     claims: list[dict], parse_status: str) -> None:
        """Merge deterministic records atomically; reimports preserve existing reviews."""
        if any(item["paper_id"] != paper_id for item in chunks + entities + claims):
            raise ValueError("Import batch contains a different source paper")
        validate_claims(chunks, entities, claims)
        with self.driver.session() as session:
            session.execute_write(self._write_paper, paper_id, chunks, entities, claims, parse_status)

    @staticmethod
    @unit_of_work(timeout=30)
    def _write_paper(tx, paper_id, chunks, entities, claims, parse_status):
        """Use bounded UNWIND batches; every query is an application-owned template."""
        expected = {paper_id} | {c["object_id"] for c in claims if c["predicate"] == "CITES"}
        actual = {r["id"] for r in tx.run(
            "MATCH (p:Paper) WHERE p.id IN $ids RETURN p.id AS id", ids=sorted(expected))}
        if expected != actual:
            raise ValueError("Register source and citation target papers before import")
        retain_pending_bibliography(tx, paper_id)

        def run(statement, rows):
            for offset in range(0, len(rows), 100):
                tx.run(statement, rows=rows[offset:offset + 100]).consume()

        run("UNWIND $rows AS row MATCH (p:Paper {id: row.paper_id}) "
            "MERGE (c:Chunk {id: row.id}) ON CREATE SET c += row "
            "MERGE (c)-[:PART_OF]->(p)", chunks)
        run("UNWIND $rows AS row MATCH (a:Chunk {id: row.source}), (b:Chunk {id: row.target}) "
            "MERGE (a)-[:NEXT]->(b)",
            [{"source": a["id"], "target": b["id"]} for a, b in zip(chunks, chunks[1:])])
        run("UNWIND $rows AS row MATCH (c:Chunk {id: row.chunk_id}) "
            "MERGE (e:Entity {id: row.id}) ON CREATE SET e.canonical_name=row.canonical_name, "
            "e.normalized_name=row.normalized_name, e.kind=row.kind, e.paper_id=row.paper_id, "
            "e.resolution_status=row.resolution_status "
            "FOREACH (_ IN CASE WHEN row.kind='Topic' THEN [1] ELSE [] END | SET e:Topic) "
            "MERGE (c)-[m:MENTIONS {start_char: row.start_char, end_char: row.end_char}]->(e) "
            "ON CREATE SET m.surface=row.canonical_name, m.validation_status='EXACT_SURFACE'", entities)
        # Labels are fixed application constants, never taken from documents or LLM output.
        for label in ("Paper", "Entity"):
            rows = [c for c in claims if (c["predicate"] == "CITES") == (label == "Paper")]
            run("UNWIND $rows AS row MATCH (p:Paper {id: row.subject_id}), "
                f"(o:{label} {{id: row.object_id}}), (chunk:Chunk {{id: row.chunk_id}}) "
                "MERGE (c:Claim {id: row.id}) ON CREATE SET c += row, c.created_at=datetime() "
                "MERGE (c)-[:SUBJECT]->(p) MERGE (c)-[:OBJECT]->(o) "
                "MERGE (c)-[s:SUPPORTED_BY]->(chunk) "
                "ON CREATE SET s.quote=row.quote, s.start_char=row.start_char, "
                "s.end_char=row.end_char, s.quote_sha256=row.quote_sha256", rows)
        # Only the current paper's derived cache is refreshed, inside the transaction.
        refresh_citations(tx, paper_id)
        tx.run("MATCH (p:Paper {id:$id}) SET p.parse_status=$status", id=paper_id, status=parse_status).consume()

    def review_claim(self, claim_id: str, reviewer: str, note: str, *, approved: bool) -> None:
        """Local operator action only: record a named student's explicit semantic decision.

        Never called by import or the LLM. This records an attestation; it cannot
        authenticate a person's identity. No real student approval is synthesized.
        """
        if (not reviewer.strip() or not note.strip() or type(approved) is not bool
                or reviewer.casefold().startswith(("automated", "assistant", "llm"))):
            raise ValueError("A named human reviewer, review note and explicit boolean decision are required")
        with self.driver.session() as session:
            session.execute_write(self._review_claim, claim_id, reviewer, note, approved)

    @staticmethod
    @unit_of_work(timeout=30)
    def _review_claim(tx, claim_id, reviewer, note, approved):
        record = tx.run(
            "MATCH (c:Claim {id:$id})-[:SUPPORTED_BY]->(chunk:Chunk) "
            "RETURN properties(c) AS claim, chunk.text AS text", id=claim_id).single(strict=True)
        claim = record["claim"]
        if record["text"][claim["start_char"]:claim["end_char"]] != claim["quote"]:
            raise ValueError("Stored supporting quote no longer matches source")
        if claim["predicate"] == "CITES" and claim.get("source_location_status") != "SOURCE_LOCATED":
            raise ValueError("Bibliography location must be checked before semantic approval")
        timestamp = datetime.now(timezone.utc).isoformat()
        status = "SOURCE_VERIFIED" if approved else "REJECTED"
        event = json.dumps({"previous_status": claim["status"], "status": status, "reviewer": reviewer,
                            "note": note, "at": timestamp}, sort_keys=True)
        tx.run(
            "MATCH (c:Claim {id:$id}) SET c.status=$status, c.human_reviewed=true, c.reviewer=$reviewer, "
            "c.reviewed_at=$at, c.review_policy=$policy, c.review_note=$note, "
            "c.student_review_status=$decision, c.review_history=coalesce(c.review_history,[])+[$event]",
            id=claim_id, status=status, reviewer=reviewer, at=timestamp, policy=HUMAN_POLICY,
            note=note, decision="approved" if approved else "rejected", event=event,
        ).consume()
        refresh_citations(tx, claim["paper_id"])

    def counts(self, paper_ids: list[str]) -> dict:
        """Measure this corpus only; never mistake test fixtures for corpus statistics."""
        nodes, _, _ = self.driver.execute_query(
            "MATCH (n) WHERE (n:Paper AND n.id IN $ids) OR n.paper_id IN $ids "
            "UNWIND labels(n) AS label RETURN label, count(*) AS count ORDER BY label", ids=paper_ids,
        )
        edges, _, _ = self.driver.execute_query(
            "MATCH (a)-[r]->() WHERE (a:Paper AND a.id IN $ids) OR a.paper_id IN $ids "
            "RETURN type(r) AS type, count(*) AS count ORDER BY type", ids=paper_ids,
        )
        statuses, _, _ = self.driver.execute_query(
            "MATCH (c:Claim) WHERE c.paper_id IN $ids "
            "RETURN c.status AS status, c.origin AS origin, count(*) AS count ORDER BY status, origin", ids=paper_ids,
        )
        return {"nodes": {r["label"]: r["count"] for r in nodes},
                "relationships": {r["type"]: r["count"] for r in edges},
                "claims": [dict(r) for r in statuses]}

    def fingerprint(self, paper_ids: list[str]) -> str:
        """Hash logical identities/properties, excluding unstable Neo4j internal IDs."""
        nodes, _, _ = self.driver.execute_query(
            "MATCH (n) WHERE (n:Paper AND n.id IN $ids) OR n.paper_id IN $ids "
            "RETURN n.id AS id, labels(n) AS labels, properties(n) AS properties ORDER BY id", ids=paper_ids,
        )
        edges, _, _ = self.driver.execute_query(
            "MATCH (a)-[r]->(b) WHERE (a:Paper AND a.id IN $ids) OR a.paper_id IN $ids "
            "RETURN a.id AS source, type(r) AS type, b.id AS target, properties(r) AS properties",
            ids=paper_ids,
        )
        node_data = [{**dict(r), "labels": sorted(r["labels"])} for r in nodes]
        edge_data = sorted(json.dumps(dict(r), sort_keys=True, default=str) for r in edges)
        return digest(json.dumps({"nodes": node_data, "edges": edge_data}, sort_keys=True, default=str))
