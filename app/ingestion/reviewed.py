"""Bounded preparation and atomic application of the documented PR #5 decisions."""

import csv
import json

import pypdf
from neo4j import unit_of_work

from app.ingestion.citations import verify_citation
from app.ingestion.documents import digest, parse_pdf, prototype_manifest, stable_id
from app.ingestion.graph import EvidenceGraph, HUMAN_POLICY, refresh_citations
from app.ingestion.research import require, verify_record, map_supports
from app.ingestion.reviews import load_decisions, resolve_alias, REVIEW_PATH
from app.ingestion.support import validate_bundle, stored_support

POLICY = "reviewed-research-v1"


def encoded(value):
    """Stable JSON for Neo4j properties and audit identities."""
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), default=str)


def sources(root):
    """Read only approved source artifacts; never evaluation gold or model outputs."""
    require(pypdf.__version__ == "6.10.0", "Requires pypdf 6.10.0")
    decisions = load_decisions(root)
    papers = prototype_manifest(root)
    pages, warnings = {}, {}
    for paper in papers:
        pages[paper["paper_id"]], warnings[paper["paper_id"]] = parse_pdf(
            root / paper["suggested_download_path"], paper
        )
    with (root / "corpus/GRAPH_EVIDENCE_CANDIDATES.csv").open(newline="") as handle:
        candidates = list(csv.DictReader(handle))
    with (root / "corpus/citation_evidence.csv").open(newline="") as handle:
        citations = [r for r in csv.DictReader(handle) if r["evidence_id"] in ("C03", "C09")]
    return dict(
        papers=papers,
        pages=pages,
        candidates=candidates,
        citations=citations,
        decisions=decisions,
        parser_warnings=warnings,
    )


def snapshot(tx, paper_ids, entity_ids):
    """Small corpus snapshot including canonical identities and all incident edges."""
    nodes = [
        dict(r)
        for r in tx.run(
            "MATCH (n) WHERE n.id IN $ids OR n.paper_id IN $papers "
            "RETURN n.id AS id,labels(n) AS labels,properties(n) AS properties ORDER BY id LIMIT 2001",
            ids=paper_ids + entity_ids,
            papers=paper_ids,
        )
    ]
    require(len(nodes) <= 2000, "Review snapshot exceeds node budget")
    ids = [n["id"] for n in nodes]
    edges = [
        dict(r)
        for r in tx.run(
            "MATCH (a)-[r]->(b) WHERE a.id IN $ids OR b.id IN $ids "
            "RETURN a.id AS source,type(r) AS type,b.id AS target,properties(r) AS properties LIMIT 6001",
            ids=ids,
        )
    ]
    require(len(edges) <= 6000, "Review snapshot exceeds edge budget")
    for n in nodes:
        n["labels"].sort()
    fingerprint = digest(encoded({"nodes": nodes, "edges": sorted(encoded(r) for r in edges)}))
    return {"nodes": nodes, "edges": edges, "fingerprint": fingerprint}


def support_parts(mapping, role, page, chunks):
    """Preserve the entire authenticated normalized span, even across chunks."""
    parts = []
    for i, span in enumerate(mapping):
        chunk = chunks[span["chunk_id"]]
        a, b = span["chunk_start"], span["chunk_end"]
        quote = chunk["text"][a:b]
        require(
            quote == page["text"][span["normalized_page_start"] : span["normalized_page_end"]],
            "Live chunk/source span mismatch",
        )
        parts.append(
            dict(
                chunk_id=chunk["id"],
                role=role,
                part=i,
                start_char=a,
                end_char=b,
                quote=quote,
                quote_sha256=digest(quote),
                page_start=span["normalized_page_start"],
                page_end=span["normalized_page_end"],
            )
        )
    return parts


def attach_support(claim, page, mapping, chunks, raw_excerpt, raw_context):
    """Keep raw provenance, normalized evidence and exact chunk-local segments."""
    parts = support_parts(mapping["excerpt_supports"], "excerpt", page, chunks)
    parts += support_parts(mapping["context_supports"], "context", page, chunks)
    first = parts[0]
    for key in ("chunk_id", "quote", "quote_sha256", "start_char", "end_char"):
        claim[key] = first[key]
    claim["support_manifest_json"] = encoded(parts)
    for role, raw_span in [("excerpt", raw_excerpt), ("context", raw_context)]:
        text = "".join(p["quote"] for p in parts if p["role"] == role)
        claim.update(
            {
                role + "_text": text,
                role + "_text_sha256": digest(text),
                "raw_" + role: page["raw_text"][raw_span[0] : raw_span[1]],
                "raw_" + role + "_start": raw_span[0],
                "raw_" + role + "_end": raw_span[1],
            }
        )
    validate_bundle(claim, parts, chunks)
    return parts


def prepare(inputs, state):
    """Pure proposed changes from independently verified files and actual graph rows."""
    papers = {p["paper_id"]: p for p in inputs["papers"]}
    decisions, pages = inputs["decisions"], inputs["pages"]
    nodes = {n["id"]: n for n in state["nodes"]}
    chunks = {n["id"]: n["properties"] for n in state["nodes"] if "Chunk" in n["labels"]}
    for ident, paper in papers.items():
        actual = nodes.get(ident, {}).get("properties", {})
        require(
            (actual.get("pdf_sha256"), actual.get("source_version"), actual.get("work_id"))
            == (paper["pdf_access"]["sha256"], paper["version"], paper["work_id"]),
            "Missing/incompatible live Paper",
        )
    for chunk in chunks.values():
        paper, number = chunk["paper_id"], chunk["page"]
        require(paper in papers and 1 <= number <= len(pages[paper]), "Incorrect chunk paper/page")
        page = pages[paper][number - 1]
        parents = [e["target"] for e in state["edges"] if e["source"] == chunk["id"] and e["type"] == "PART_OF"]
        require(
            parents == [paper]
            and chunk["pdf_sha256"] == papers[paper]["pdf_access"]["sha256"]
            and chunk["page_raw_sha256"] == page["raw_sha256"],
            "Incorrect chunk source association",
        )
        require(
            page["text"][chunk["start_char"] : chunk["end_char"]] == chunk["text"]
            and digest(chunk["text"]) == chunk["text_sha256"],
            "Live chunk text/hash/offset mismatch",
        )
    mapped = [
        dict(id=c["id"], paper=c["paper_id"], page=c["page"], start=c["start_char"], end=c["end_char"])
        for c in chunks.values()
    ]
    entities, claims, supports, deferred = {}, [], {}, []
    for row in inputs["candidates"]:
        ident, paper_id = row["candidate_id"], row["source_paper_id"]
        alias_id, alias = resolve_alias(decisions, row)
        paper = papers[paper_id]
        require(
            row["subject_kind"] == "Paper"
            and row["subject_id"] == paper_id
            and row["pdf_sha256"] == paper["pdf_access"]["sha256"]
            and row["pdf_url"] == paper["pdf_url"] + "#page=" + row["pdf_page_1based"]
            and (row["parser"], row["parser_version"]) == ("pypdf", "6.10.0"),
            "Candidate source mismatch",
        )
        mapping = verify_record(row, "candidate", pages, mapped)
        page = pages[paper_id][mapping["pdf_page"] - 1]
        entity_id = alias["canonical_id"]
        entity = entities.setdefault(
            entity_id,
            dict(
                id=entity_id,
                kind=row["object_kind"],
                canonical_name=row["normalized_proposed_entity_name"],
                normalized_name=row["normalized_proposed_entity_name"].casefold(),
                resolution_status="STUDENT_APPROVED_SCOPED",
                alias_decision_id=alias_id,
                alias_review_json=encoded(alias),
                review_document=REVIEW_PATH,
                review_document_sha256=decisions["inputs_sha256"][REVIEW_PATH],
                source_paper_ids=[],
            ),
        )
        require(
            entity["kind"] == row["object_kind"] and entity["canonical_name"] == row["normalized_proposed_entity_name"],
            "Ambiguous canonical entity",
        )
        entity["source_paper_ids"] = sorted(set(entity["source_paper_ids"] + [paper_id]))
        claim = dict(
            id=stable_id(POLICY, paper_id, row["pdf_sha256"], ident),
            evidence_id=ident,
            paper_id=paper_id,
            subject_id=paper_id,
            object_id=entity_id,
            object_kind=row["object_kind"],
            predicate=row["predicate"],
            status="EXTRACTED",
            student_review_status="pending",
            origin="DOCUMENTED_RESEARCH",
            research_origin=row["research_origin"],
            source_location_status="SOURCE_LOCATED",
            source_pdf_sha256=row["pdf_sha256"],
            source_url=paper["pdf_url"],
            source_version=paper["version"],
            page=mapping["pdf_page"],
            page_raw_sha256=row["page_text_sha256"],
            source_surface=row["object_surface_form"],
            alias_decision_id=alias_id,
            source_qualifier=row["qualifier"],
            source_ambiguity=row["ambiguity"],
        )
        if ident == "GE20":
            claim.update(evaluation_stage="entity_extraction", evaluation_scope="COMPONENT_ONLY")
        supports[claim["id"]] = attach_support(
            claim, page, mapping, chunks, mapping["raw_excerpt"], mapping["raw_context"]
        )
        claims.append(claim)
    for row in inputs["citations"]:
        source, target = papers[row["source_paper_id"]], papers[row["selected_target_paper_id"]]
        claim = verify_citation(
            row,
            source,
            target,
            pages[source["paper_id"]],
            [c for c in chunks.values() if c["paper_id"] == source["paper_id"]],
        )
        claim["source_version"] = source["version"]
        page = pages[source["paper_id"]][claim["page"] - 1]
        a, b = claim["reference_raw_start"], claim["reference_raw_end"]
        context = claim["reference_context"]
        c = page["raw_text"].find(context)
        require(c >= 0 and page["raw_text"].find(context, c + 1) == -1, "Ambiguous bibliography context")
        d = c + len(context)
        mapping = {
            "excerpt_supports": map_supports(mapped, pages, source["paper_id"], claim["page"], a, b),
            "context_supports": map_supports(mapped, pages, source["paper_id"], claim["page"], c, d),
        }
        supports[claim["id"]] = attach_support(claim, page, mapping, chunks, (a, b), (c, d))
        claims.append(claim)
    require(len(claims) == 22 and len({c["evidence_id"] for c in claims}) == 22, "Incomplete claim batch")
    changes = []
    for claim in claims:
        decision = decisions["claims"][claim["evidence_id"]]
        claim.update(
            accepted_qualification=decision["accepted_scope"],
            review_context_json=encoded(decision["review_context"]),
            reviewed_source_locations=decision["inspected_sources"],
            integration_policy=POLICY,
        )
        claim["decision_sha256"] = digest(encoded(decision))
        existing = [
            n
            for n in state["nodes"]
            if "Claim" in n["labels"]
            and (n["id"] == claim["id"] or n["properties"].get("evidence_id") == claim["evidence_id"])
        ]
        require(len(existing) <= 1, "Duplicate existing evidence identity")
        action = "CREATE_AND_RECORD_APPROVAL"
        if existing:
            old = existing[0]["properties"]
            require(
                old["id"] == claim["id"]
                and all(
                    old[k] == claim[k]
                    for k in ("paper_id", "subject_id", "object_id", "predicate", "quote", "quote_sha256", "page")
                ),
                "Existing evidence conflicts with reviewed assertion",
            )
            old_edges = [e for e in state["edges"] if e["source"] == claim["id"]]
            require(
                [e["target"] for e in old_edges if e["type"] == "SUBJECT"] == [claim["subject_id"]]
                and [e["target"] for e in old_edges if e["type"] == "OBJECT"] == [claim["object_id"]],
                "Existing claim endpoint association mismatch",
            )
            old_supports = [
                dict(e["properties"], chunk_id=e["target"]) for e in old_edges if e["type"] == "SUPPORTED_BY"
            ]
            if old.get("support_manifest_json"):
                validate_bundle(old, old_supports, chunks)
            else:
                require(
                    len(old_supports) == 1
                    and old_supports[0]
                    == {k: old[k] for k in ("chunk_id", "quote", "quote_sha256", "start_char", "end_char")},
                    "Existing citation support mismatch",
                )
                ch = chunks[old["chunk_id"]]
                require(
                    ch["paper_id"] == old["paper_id"]
                    and ch["text"][old["start_char"] : old["end_char"]] == old["quote"],
                    "Existing citation quote mismatch",
                )
            final = old.get("human_reviewed") or old.get("status") in ("SOURCE_VERIFIED", "REJECTED")
            if final:
                require(
                    old.get("status") == "SOURCE_VERIFIED"
                    and old.get("review_policy") == HUMAN_POLICY
                    and old.get("human_reviewed") is True
                    and old.get("student_review_status") == "approved"
                    and old.get("reviewer") == decision["reviewer"]
                    and old.get("decision_sha256") == claim["decision_sha256"]
                    and old.get("signoff_recorded_date") == decision["signoff_recorded_date"]
                    and old.get("review_document_sha256") == decisions["inputs_sha256"][REVIEW_PATH]
                    and bool(old.get("reviewed_at"))
                    and old.get("review_applied_at") == old["reviewed_at"],
                    "Existing approved/rejected decision cannot be overwritten",
                )
                require(
                    all(old.get(k) == v for k, v in claim.items() if k not in ("status", "student_review_status")),
                    "Reviewed claim has changed",
                )
                action = "REUSE_APPROVED"
            else:
                action = "REUSE_PENDING_AND_RECORD_APPROVAL"
        changes.append(
            dict(
                evidence_id=claim["evidence_id"],
                claim_id=claim["id"],
                paper_id=claim["paper_id"],
                target_id=claim["object_id"],
                predicate=claim["predicate"],
                page=claim["page"],
                chunk_ids=sorted({s["chunk_id"] for s in supports[claim["id"]]}),
                student_decision=decision["decision"],
                reviewer=decision["reviewer"],
                signoff_recorded_date=decision["signoff_recorded_date"],
                accepted_qualification=claim["accepted_qualification"],
                source_qualifier=claim.get("source_qualifier"),
                readiness="READY_AFTER_OPERATOR_AUTHORIZATION",
                action=action,
            )
        )
    for entity in entities.values():
        if entity["id"] in nodes:
            require(
                all(nodes[entity["id"]]["properties"].get(k) == v for k, v in entity.items()),
                "Existing canonical identity/alias decision conflicts",
            )
    return dict(
        claims=claims,
        entities=list(entities.values()),
        supports=supports,
        changes=changes,
        aliases=decisions["aliases"],
        deferred=deferred,
    )


class ReviewedImporter:
    """One operator transaction; preparation alone never writes or grants approval."""

    def __init__(self, driver, inputs):
        self.driver, self.inputs = driver, inputs
        self.paper_ids = [p["paper_id"] for p in inputs["papers"]]
        self.entity_ids = [a["canonical_id"] for a in inputs["decisions"]["aliases"].values() if a["canonical_id"]]

    def inspect(self):
        """Read the scoped graph snapshot and fingerprint without changing review state."""
        with self.driver.session(default_access_mode="READ") as session:
            return session.execute_read(self._snapshot)

    @unit_of_work(timeout=30)
    def _snapshot(self, tx):
        return snapshot(tx, self.paper_ids, self.entity_ids)

    def dry_run(self):
        """Prepare proposed actions and reject concurrent graph changes without writing."""
        state = self.inspect()
        plan = prepare(self.inputs, state)
        require(self.inspect()["fingerprint"] == state["fingerprint"], "Graph changed during dry-run")
        return state, plan

    def apply(self, expected_fingerprint):
        """Call only after explicit operator authorization; never called by dry-run."""
        with self.driver.session() as session:
            return session.execute_write(self._apply, expected_fingerprint)

    @unit_of_work(timeout=30)
    def _apply(self, tx, expected_fingerprint):
        # Serialize this operator batch on its existing source papers (no new lock node).
        for ident in sorted(self.paper_ids):
            tx.run("MATCH (p:Paper {id:$id}) SET p.id=p.id", id=ident).consume()
        state = snapshot(tx, self.paper_ids, self.entity_ids)
        require(state["fingerprint"] == expected_fingerprint, "Graph changed since inspected dry-run")
        plan = prepare(self.inputs, state)
        decisions = self.inputs["decisions"]
        for entity in plan["entities"]:
            tx.run(
                "MERGE (e:Entity {id:$id}) ON CREATE SET e += $properties", id=entity["id"], properties=entity
            ).consume()
        actions = {r["claim_id"]: r["action"] for r in plan["changes"]}
        graph = EvidenceGraph(self.driver)
        for claim in plan["claims"]:
            if actions[claim["id"]] == "REUSE_APPROVED":
                stored_support(tx, claim["id"])
                continue
            old = next((n["properties"] for n in state["nodes"] if n["id"] == claim["id"]), None)
            if old:
                tx.run(
                    "MATCH (c:Claim {id:$id}) SET "
                    "c.prior_evidence_history=coalesce(c.prior_evidence_history,[])+[$event]",
                    id=claim["id"],
                    event=encoded(
                        {
                            "claim": old,
                            "supports": [
                                e for e in state["edges"] if e["source"] == claim["id"] and e["type"] == "SUPPORTED_BY"
                            ],
                        }
                    ),
                ).consume()
            # Old pending C03/C09 quote/source fields were checked above, not discarded.
            tx.run(
                "MERGE (c:Claim {id:$id}) ON CREATE SET c.created_at=datetime() " "SET c += $properties",
                id=claim["id"],
                properties=claim,
            ).consume()
            target_label = "Paper" if claim["predicate"] == "CITES" else "Entity"
            tx.run(
                "MATCH (c:Claim {id:$id}),(p:Paper {id:$paper}),"
                f"(o:{target_label} {{id:$target}}) "
                "MERGE (c)-[:SUBJECT]->(p) MERGE (c)-[:OBJECT]->(o)",
                id=claim["id"],
                paper=claim["paper_id"],
                target=claim["object_id"],
            ).consume()
            # Retain original pending evidence in history before replacing its single
            # title support with the fully authenticated excerpt + context bundle.
            tx.run("MATCH (:Claim {id:$id})-[s:SUPPORTED_BY]->() DELETE s", id=claim["id"]).consume()
            for support in plan["supports"][claim["id"]]:
                properties = {k: v for k, v in support.items() if k != "chunk_id"}
                tx.run(
                    "MATCH (c:Claim {id:$id}),(chunk:Chunk {id:$chunk}) "
                    "CREATE (c)-[s:SUPPORTED_BY]->(chunk) SET s=$properties",
                    id=claim["id"],
                    chunk=support["chunk_id"],
                    properties=properties,
                ).consume()
            decision = decisions["claims"][claim["evidence_id"]]
            provenance = dict(
                review_document=REVIEW_PATH,
                review_document_sha256=decisions["inputs_sha256"][REVIEW_PATH],
                signoff_recorded_date=decision["signoff_recorded_date"],
                signoff_timezone="Europe/Paris",
                decision_sha256=claim["decision_sha256"],
            )
            graph.review_claim(
                claim["id"],
                decision["reviewer"],
                decision["accepted_scope"],
                approved=True,
                provenance=provenance,
                transaction=tx,
            )
        for paper in self.paper_ids:
            refresh_citations(tx, paper)
        return plan["changes"]
