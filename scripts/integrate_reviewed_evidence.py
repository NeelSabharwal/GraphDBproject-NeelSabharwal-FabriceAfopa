"""Operator CLI: validate/dry-run by default; --apply needs separate human authorization.

Reads the signed research artifacts, never evaluation gold. JSON goes to stdout so
the host can retain an ignored audit report without mounting writable source data.
"""

import argparse
from collections import Counter
import json
from pathlib import Path

from neo4j import GraphDatabase

from app.config import Settings
from app.ingestion.reviewed import ReviewedImporter, sources
from app.ingestion.research import require


def report(state, plan):
    """Expose exact additions/reuse, qualifications and negative alias decisions."""
    return dict(
        graph_fingerprint=state["fingerprint"],
        node_counts=dict(Counter(label for n in state["nodes"] for label in n["labels"])),
        relationship_counts=dict(Counter(e["type"] for e in state["edges"])),
        changes=plan["changes"],
        aliases=plan["aliases"],
        deferred=plan["deferred"],
        proposed_claim_records=plan["claims"],
        proposed_supports=plan["supports"],
        proposed_new_entities=[e for e in plan["entities"] if e["id"] not in {n["id"] for n in state["nodes"]}],
        proposed_reused_entities=[e["id"] for e in plan["entities"] if e["id"] in {n["id"] for n in state["nodes"]}],
        actions=dict(Counter(r["action"] for r in plan["changes"])),
        support_relationships=sum(len(s) for s in plan["supports"].values()),
    )


def verify_applied(importer, state, plan):
    """Read actual reviewed assertions/joins/edges, only after a real apply exists."""
    require(
        all(c["action"] == "REUSE_APPROVED" for c in plan["changes"]),
        "Reviewed integration not fully applied; no positive real-graph result is claimed",
    )
    claims = {c["id"]: c for c in plan["claims"]}
    scientific = [
        dict(
            evidence_id=c["evidence_id"],
            source=c["subject_id"],
            target=c["object_id"],
            predicate=c["predicate"],
            qualification=c["accepted_qualification"],
        )
        for c in claims.values()
        if c["predicate"] != "CITES"
    ]
    citations = [e for e in state["edges"] if e["type"] == "CITES"]
    for c in claims.values():
        if c["predicate"] == "CITES":
            require(
                any(
                    e["source"] == c["subject_id"]
                    and e["target"] == c["object_id"]
                    and c["id"] in e["properties"]["claim_ids"]
                    and e["properties"]["target_work_id"] == c["target_work_id"]
                    and e["properties"]["target_version_as_cited"] == "unspecified"
                    for e in citations
                ),
                "Approved citation edge missing or incompatible",
            )
    with importer.driver.session(default_access_mode="READ") as session:
        paths = [
            dict(r)
            for r in session.run(
                "MATCH path=(p:Paper {id:$source})-[:CITES*2]->(q:Paper {id:$target}) "
                "RETURN [n IN nodes(path) | n.id] AS papers, "
                "[r IN relationships(path) | r.claim_ids] AS claim_ids LIMIT 2",
                source=next(c["subject_id"] for c in claims.values() if c["evidence_id"] == "C09"),
                target=next(c["object_id"] for c in claims.values() if c["evidence_id"] == "C03"),
            )
        ]
    require(len(paths) == 1, "Expected one actual two-edge citation path")
    by_dataset = {}
    for c in claims.values():
        if c["predicate"] == "EVALUATED_ON":
            by_dataset.setdefault(c["object_id"], []).append(c["subject_id"])
    return dict(
        scientific_assertions=scientific,
        citation_edges=citations,
        actual_paths=paths,
        shared_datasets={k: sorted(set(v)) for k, v in by_dataset.items() if len(set(v)) > 1},
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--verify", action="store_true", help="Read-only verification after authorized application")
    parser.add_argument("--expected-fingerprint", help="Required for --apply; copy from reviewed dry-run")
    args = parser.parse_args(argv)
    if args.apply and not args.expected_fingerprint:
        parser.error("--apply requires the reviewed --expected-fingerprint")
    config = Settings.from_environment()
    try:
        inputs = sources(args.root.resolve())
        with GraphDatabase.driver(
            config.neo4j_uri,
            auth=(config.neo4j_user, config.neo4j_password.get_secret_value()),
            connection_timeout=5,
            max_transaction_retry_time=0,
        ) as driver:
            importer = ReviewedImporter(driver, inputs)
            state, plan = importer.dry_run()
            result = report(state, plan)
            result.update(
                mode="DRY_RUN",
                graph_unchanged=True,
                parser="6.10.0",
                parser_warnings=inputs["parser_warnings"],
                inputs_sha256=inputs["decisions"]["inputs_sha256"],
            )
            if args.apply:
                require(state["fingerprint"] == args.expected_fingerprint, "Dry-run fingerprint is stale")
                importer.apply(args.expected_fingerprint)
                after, applied = importer.dry_run()
                result.update(
                    mode="APPLIED",
                    graph_unchanged=after["fingerprint"] == state["fingerprint"],
                    after=report(after, applied),
                    verification=verify_applied(importer, after, applied),
                )
            elif args.verify:
                result.update(mode="VERIFY", verification=verify_applied(importer, state, plan))
            print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (ValueError, KeyError, IndexError, StopIteration) as error:
        print(json.dumps({"status": "FAILED", "error": str(error), "mode": "APPLY" if args.apply else "READ_ONLY"}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
