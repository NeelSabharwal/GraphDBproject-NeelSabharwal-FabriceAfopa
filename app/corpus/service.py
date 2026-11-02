"""Fixed corpus import policy; never expose paths, Cypher or review writes to clients."""

from pathlib import Path

from neo4j import GraphDatabase, Query, READ_ACCESS

from app.analytics.service import GraphService, UnknownPaper
from app.ingestion.documents import prototype_manifest
from scripts.ingest import run

CATALOG = """
MATCH (p:Paper) WHERE p.id IN $papers
OPTIONAL MATCH (c:Chunk)-[:PART_OF]->(p)
RETURN p.id AS paper_id, p.title AS title, p.work_id AS work_id,
       p.source_version AS source_version, p.pdf_sha256 AS pdf_sha256,
       p.parse_status AS parse_status,
       count(DISTINCT c) AS chunks
ORDER BY paper_id
"""


class CorpusConflict(RuntimeError):
    """An existing partial or inconsistent corpus requires operator investigation."""


def import_corpus(settings, sample_per_paper):
    """Reuse the validated importer only for an empty corpus; preserve existing reviews.

    Import is per-paper transactional, as in the CLI. A partial failure is explicit
    and subsequent HTTP retries require operator recovery, never an automatic reset.
    """
    root = Path(settings.corpus_root)
    manifest = prototype_manifest(root)
    with GraphDatabase.driver(
        settings.neo4j_uri,
        auth=(settings.neo4j_user, settings.neo4j_password.get_secret_value()),
        connection_timeout=5,
        max_transaction_retry_time=0,
    ) as driver:
        with driver.session(default_access_mode=READ_ACCESS) as session:
            rows = session.run(Query(CATALOG, timeout=5), papers=[p["paper_id"] for p in manifest]).data()
        if rows:
            expected = {p["paper_id"]: p for p in manifest}
            complete = len(rows) == len(expected) and all(
                r["pdf_sha256"] == expected[r["paper_id"]]["pdf_access"]["sha256"]
                and r["chunks"] > 0
                and r["parse_status"] in {"PARSED_WITH_WARNINGS", "PARSED_NOT_VISUALLY_REVIEWED"}
                for r in rows
            )
            if not complete:
                raise CorpusConflict("Existing corpus is partial or inconsistent; inspect the ingestion CLI audit")
            return {
                "status": "ALREADY_PRESENT",
                "papers": rows,
                "extraction_status": "NOT_REQUESTED",
                "detail": "Pinned papers already imported; no writes or extraction repeated",
            }
    report = run(root, sample_per_paper)
    return {
        "status": report["overall_status"],
        "run_id": report["run_id"],
        "import_status": report["import_status"],
        "extraction_status": report["extraction_status"],
        "detail": "See the private ingestion audit for per-paper results; import never approves claims",
    }


class CorpusService(GraphService):
    """Reuse the reviewed graph validator and its bounded read-only query runner."""

    async def catalog(self):
        """Return actual paper metadata without text, embeddings or annotations."""
        return await self.tools.read(CATALOG, papers=self.paper_ids)

    async def topic(self, ident, depth):
        """Traverse Entity <- OBJECT - approved Claim [- SUBJECT -> Paper]."""
        snap = await self.snapshot()
        if ident not in snap["entities"]:
            raise UnknownPaper("No supported, approved concept with this ID in the selected corpus")
        entity = snap["entities"][ident]
        nodes = [{"id": ident, "label": "Entity", "name": entity["canonical_name"]}]
        edges, ids = [], set()
        papers = {p["id"]: p for p in snap["papers"]}
        for claim in sorted(snap["claims"].values(), key=lambda c: c["id"]):
            if claim["object_id"] != ident:
                continue
            ids.add(claim["id"])
            nodes.append({"id": claim["id"], "label": "Claim", "name": claim["predicate"]})
            edges.append({"source": claim["id"], "target": ident, "type": "OBJECT"})
            if depth == 2:
                paper = papers[claim["paper_id"]]
                if paper["id"] not in {n["id"] for n in nodes}:
                    nodes.append({"id": paper["id"], "label": "Paper", "name": paper["title"]})
                edges.append({"source": claim["id"], "target": paper["id"], "type": "SUBJECT"})
        await self.ensure_review_unchanged(snap)
        return dict(entity_id=ident, depth=depth, nodes=nodes, edges=edges, **self.support_subset(snap, ids))
