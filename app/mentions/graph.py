"""Atomic occurrence enrichment; never creates nodes, Claims or review actions."""

from neo4j import READ_ACCESS

from app.analytics.service import accepted_entity
from app.ingestion.documents import digest
from app.ingestion.research import require
from app.mentions.matcher import VERSION
from app.mentions.source import POLICY_SHA256, PROPOSAL_SHA256, fingerprint, read_state

BATCH = "mentions-v4-" + PROPOSAL_SHA256[:16]


def properties(row):
    """Persist source provenance and mechanical status, without class labels/context."""
    keys = (
        "proposal_id",
        "surface",
        "start_char",
        "end_char",
        "text_sha256",
        "pdf_sha256",
        "pdf_page_1based",
        "page_start_char",
        "page_end_char",
        "page_raw_sha256",
        "raw_start_char",
        "raw_end_char",
        "alias_id",
        "match_policy",
        "identity_scope",
    )
    return {
        **{k: row[k] for k in keys},
        "batch_id": BATCH,
        "policy_sha256": POLICY_SHA256,
        "proposal_sha256": PROPOSAL_SHA256,
        "validation": "EXACT_SURFACE",
        "student_review_status": "NOT_REVIEWED",
        "origin": "DETERMINISTIC_SOURCE_MATCH",
    }


class MentionImporter:
    """One explicit transaction, no managed retries; stale/conflicting state fails closed."""

    def __init__(self, driver):
        self.driver = driver

    @staticmethod
    def plan(tx, rows):
        """Authenticate every endpoint before writing even the first occurrence."""
        require(
            len(rows) <= 1000 and len({r["proposal_id"] for r in rows}) == len(rows),
            "Duplicate or excessive proposal rows",
        )
        new, reused = [], []
        for row in rows:
            records = tx.run(
                "MATCH (c:Chunk {id:$chunk}) MATCH (e:Entity {id:$entity}) "
                "OPTIONAL MATCH (c)-[:PART_OF]->(p:Paper) "
                "WITH c,e,collect(p{.id,.pdf_sha256}) AS parents "
                "OPTIONAL MATCH (c)-[m:MENTIONS]->(e) WHERE m.start_char=$start AND m.end_char=$end "
                "RETURN c{.text,.text_sha256,.paper_id,.pdf_sha256,.page,.start_char,.page_raw_sha256} AS c, "
                "properties(e) AS e, parents, collect(properties(m)) AS mentions",
                chunk=row["chunk_id"],
                entity=row["entity_id"],
                start=row["start_char"],
                end=row["end_char"],
            ).data()
            require(len(records) == 1, "Missing or duplicate occurrence endpoint")
            record = records[0]
            chunk, entity = record["c"], record["e"]
            require(
                record["parents"] == [{"id": row["paper_id"], "pdf_sha256": row["pdf_sha256"]}]
                and chunk["paper_id"] == row["paper_id"],
                "Invalid occurrence Paper membership",
            )
            require(
                chunk["pdf_sha256"] == row["pdf_sha256"]
                and chunk["page"] == row["pdf_page_1based"]
                and chunk["page_raw_sha256"] == row["page_raw_sha256"],
                "Source provenance mismatch",
            )
            require(digest(chunk["text"]) == chunk["text_sha256"] == row["text_sha256"], "Source text hash mismatch")
            require(
                0 <= row["start_char"] < row["end_char"] <= len(chunk["text"])
                and chunk["text"][row["start_char"] : row["end_char"]] == row["surface"],
                "Invalid exact surface",
            )
            require(
                row["page_start_char"] == chunk["start_char"] + row["start_char"]
                and row["page_end_char"] == chunk["start_char"] + row["end_char"],
                "Page offsets disagree",
            )
            require(
                accepted_entity(entity)
                and entity["kind"] == row["kind"]
                and entity["alias_decision_id"] == row["alias_id"]
                and row["match_policy"] == VERSION,
                "Unapproved/scoped identity mismatch",
            )
            require(len(record["mentions"]) <= 1, "Duplicate existing occurrence")
            if record["mentions"]:
                require(record["mentions"][0] == properties(row), "Conflicting existing occurrence; no overwrite")
                reused.append(row["proposal_id"])
            else:
                new.append(row)
        return new, reused

    def dry_run(self, rows):
        """Report current fingerprint and insert/reuse counts with no writes."""
        with self.driver.session(default_access_mode=READ_ACCESS) as session:
            with session.begin_transaction(timeout=30) as tx:
                current = fingerprint(read_state(tx))
                new, reused = self.plan(tx, rows)
                tx.rollback()
        return {"fingerprint": current, "proposed_new": len(new), "reused": len(reused), "mutation": False}

    @staticmethod
    def _create(tx, row):
        result = tx.run(
            "MATCH (c:Chunk {id:$chunk}), (e:Entity {id:$entity}) "
            "CREATE (c)-[m:MENTIONS]->(e) SET m=$props RETURN m.proposal_id AS id",
            chunk=row["chunk_id"],
            entity=row["entity_id"],
            props=properties(row),
        ).single()
        require(result and result["id"] == row["proposal_id"], "Occurrence creation failed")

    def apply(self, rows, expected_fingerprint):
        """Apply only the inspected state; exceptions roll back the complete batch."""
        with self.driver.session() as session:
            with session.begin_transaction(timeout=30) as tx:
                require(fingerprint(read_state(tx)) == expected_fingerprint, "Stale graph fingerprint")
                new, reused = self.plan(tx, rows)
                for row in new:
                    self._create(tx, row)
                remaining, now_reused = self.plan(tx, rows)
                require(not remaining and len(now_reused) == len(rows), "Post-write verification failed")
                tx.commit()
        return {
            "batch_id": BATCH,
            "created_ids": [r["proposal_id"] for r in new],
            "reused_ids": reused,
            "committed": True,
            "before_fingerprint": expected_fingerprint,
        }

    def rollback(self, receipt):
        """Remove only batch-owned edges actually created by the supplied receipt."""
        require(receipt["batch_id"] == BATCH and receipt.get("committed") is True, "Invalid receipt")
        ids = receipt["created_ids"]
        require(len(ids) == len(set(ids)) <= 1000, "Invalid rollback occurrence list")
        with self.driver.session() as session:
            with session.begin_transaction(timeout=30) as tx:
                rows = tx.run(
                    "MATCH ()-[m:MENTIONS]->() WHERE m.proposal_id IN $ids " "RETURN properties(m) AS m", ids=ids
                ).data()
                require(
                    all(
                        r["m"].get("batch_id") == BATCH and r["m"].get("proposal_sha256") == PROPOSAL_SHA256
                        for r in rows
                    ),
                    "Rollback ownership mismatch",
                )
                tx.run(
                    "MATCH ()-[m:MENTIONS]->() WHERE m.proposal_id IN $ids AND m.batch_id=$batch " "DELETE m",
                    ids=ids,
                    batch=BATCH,
                ).consume()
                tx.commit()
        return {"removed": len(rows)}
