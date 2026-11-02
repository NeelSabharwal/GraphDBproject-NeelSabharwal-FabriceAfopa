"""Dry-run or explicitly apply the frozen, source-authenticated mention batch."""

import argparse
import hashlib
import json
from pathlib import Path

from neo4j import GraphDatabase

from app.config import Settings
from app.ingestion.research import require
from app.mentions.graph import BATCH, MentionImporter
from app.mentions.source import BASELINE_SHA256, fingerprint, prepare, snapshot


def main():
    """Default is read-only; apply requires a fresh fingerprint and backup receipt."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("/workspace"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--fingerprint")
    parser.add_argument("--backup-receipt", type=Path)
    args = parser.parse_args()
    require(not args.output.exists(), "Refusing to overwrite an audit report")
    settings = Settings.from_environment()
    with GraphDatabase.driver(
        settings.neo4j_uri,
        auth=(settings.neo4j_user, settings.neo4j_password.get_secret_value()),
        connection_timeout=5,
        max_transaction_retry_time=0,
    ) as driver:
        before = snapshot(driver)
        protected = {
            **before,
            "relationships": [
                r
                for r in before["relationships"]
                if not (r["type"] == "MENTIONS" and r["properties"].get("batch_id") == BATCH)
            ],
        }
        require(fingerprint(protected) == BASELINE_SHA256, "Protected graph differs from authorized baseline")
        rows, source = prepare(args.root, before)
        importer = MentionImporter(driver)
        report = dict(source=source, dry_run=importer.dry_run(rows))
        if args.apply:
            require(args.fingerprint and args.backup_receipt, "Apply requires fingerprint and verified backup receipt")
            backup = json.loads(args.backup_receipt.read_text())
            require(
                backup.get("integrity_verified") is True
                and backup.get("size_bytes", 0) > 0
                and backup.get("sha256")
                and backup.get("baseline_fingerprint") == args.fingerprint,
                "Invalid backup receipt",
            )
            archive = args.root / backup["archive"]
            require(archive.is_file() and archive.stat().st_size == backup["size_bytes"], "Backup archive unavailable")
            with archive.open("rb") as handle:
                require(
                    hashlib.file_digest(handle, "sha256").hexdigest() == backup["sha256"],
                    "Backup archive checksum changed",
                )
            # The operator supplies an inspected backup receipt; this CLI never restores automatically.
            report["application"] = importer.apply(rows, args.fingerprint)
        after = snapshot(driver)
        remaining = importer.dry_run(rows)
        protected_after = {
            **after,
            "relationships": [
                r
                for r in after["relationships"]
                if not (r["type"] == "MENTIONS" and r["properties"].get("batch_id") == BATCH)
            ],
        }
        require(fingerprint(protected_after) == BASELINE_SHA256, "Protected graph changed")
        report.update(
            after_fingerprint=fingerprint(after),
            post_dry_run=remaining,
            protected_fingerprint=fingerprint(protected_after),
            mentions_total=sum(r["type"] == "MENTIONS" for r in after["relationships"]),
        )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
