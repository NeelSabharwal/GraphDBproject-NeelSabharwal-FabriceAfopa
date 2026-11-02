"""Train the frozen educational pilot on authenticated live graph features."""

import argparse
import json
from pathlib import Path
import platform

import joblib
from neo4j import GraphDatabase
import sklearn

from app.config import Settings
from app.ingestion.documents import digest
from app.ingestion.research import require
from app.mentions.graph import MentionImporter
from app.mentions.source import fingerprint, prepare, snapshot
from app.ml.features import extract_features
from app.ml.pilot import SETTINGS, experiment, labels


def main():
    """Write only ignored experiment artifacts; never persist predictions to Neo4j."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("/workspace"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    # Record settings before touching labels or observing any model performance.
    (args.output / "settings.json").write_text(json.dumps(SETTINGS, indent=2) + "\n")
    config = Settings.from_environment()
    with GraphDatabase.driver(
        config.neo4j_uri,
        auth=(config.neo4j_user, config.neo4j_password.get_secret_value()),
        max_transaction_retry_time=0,
    ) as driver:
        before = snapshot(driver)
        proposals, source = prepare(args.root, before)
        plan = MentionImporter(driver).dry_run(proposals)
        require(plan["proposed_new"] == 0 and plan["reused"] == 145, "Controlled mention enrichment incomplete")
        records = extract_features(before)
        approved = labels(args.root / "data/ml/chunk_label_candidates.csv", records)
        model, report = experiment(records, approved)
        after = snapshot(driver)
        require(fingerprint(before) == fingerprint(after), "Database changed during experiment")
    report.update(
        graph_fingerprint=fingerprint(before),
        source=source,
        python=platform.python_version(),
        sklearn=sklearn.__version__,
        annotation_sha256=digest((args.root / "data/ml/chunk_label_candidates.csv").read_bytes()),
        limitations=[
            "3 papers; 15 development-visible labels; 5 held-out examples",
            "Named-entity indicators and overlapping windows; exploratory, not generalization evidence",
            "Original 8-paper/96-label target unmet",
        ],
    )
    (args.output / "features.json").write_text(json.dumps(records, indent=2) + "\n")
    (args.output / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    joblib.dump(model, args.output / "model.joblib")
    (args.output / "model.sha256").write_text(digest((args.output / "model.joblib").read_bytes()) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
