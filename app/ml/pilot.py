"""Frozen exploratory 10-train/5-test pilot; annotations never become graph properties."""

from collections import Counter
import csv
import time

import numpy as np
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, precision_recall_fscore_support
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from app.ingestion.research import require
from app.ml.features import FEATURES

TRAIN_PAPERS = ("arxiv:2004.04906v1", "arxiv:2005.11401v1")
TEST_PAPER = "arxiv:2404.16130v1"
ELIGIBLE = {
    "ML01",
    "ML03",
    "ML04",
    "ML05",
    "ML06",
    "ML08",
    "ML09",
    "ML11",
    "ML12",
    "ML13",
    "ML15",
    "ML16",
    "ML18",
    "ML19",
    "ML20",
}
SETTINGS = {"penalty": "l2", "C": 1.0, "random_state": 42, "solver": "liblinear", "max_iter": 1000, "threshold": 0.5}
CLASSES = ("METHOD", "EVALUATION")


def labels(path, records):
    """Require the exact independently approved pilot identities and hashes."""
    by_id = {r["chunk_id"]: r for r in records}
    with path.open(newline="") as stream:
        candidates = list(csv.DictReader(stream))
    require(len(candidates) == 21 and len({r["candidate_id"] for r in candidates}) == 21, "Invalid candidate table")
    approved = []
    for row in candidates:
        if row["candidate_id"] not in ELIGIBLE:
            require(row["training_eligibility"] in {"EXCLUDED", "UNRESOLVED_NOT_TRAINING"}, "Unexpected eligibility")
            continue
        require(
            row["training_eligibility"] == "ELIGIBLE_REVIEWED_PILOT"
            and row["independent_review_status"] == row["whole_chunk_approval"] == "APPROVED"
            and row["independent_reviewer"] == "NeelSabharwal"
            and row["independent_review_date"] == "2026-10-22"
            and row["actual_chunk_role_verified"] == "YES"
            and row["mapping_status"] == "UNAMBIGUOUS_MATCH"
            and row["supporting_chunk_ids"] == row["chunk_id"]
            and row["proposed_split"] == "DEVELOPMENT_ONLY",
            "Unapproved or unresolved whole-Chunk label",
        )
        source = by_id.get(row["chunk_id"])
        require(
            source
            and source["paper_id"] == row["paper_id"]
            and source["pdf_sha256"] == row["pdf_sha256"]
            and source["text_sha256"] == row["mapped_chunk_text_sha256"],
            "Label/source identity mismatch",
        )
        label = row["approved_whole_chunk_label"]
        require(label in CLASSES and label == row["proposed_whole_chunk_label"], "Invalid approved label")
        approved.append(
            {
                "candidate_id": row["candidate_id"],
                "chunk_id": row["chunk_id"],
                "paper_id": row["paper_id"],
                "label": label,
            }
        )
    require(len(approved) == len({r["chunk_id"] for r in approved}) == 15, "Expected 15 distinct approved Chunks")
    require(Counter(r["label"] for r in approved) == {"METHOD": 6, "EVALUATION": 9}, "Unexpected class counts")
    return approved


def metrics(truth, predicted):
    """Fixed class order and zero-division policy, including undefined cases."""
    precision, recall, f1, support = precision_recall_fscore_support(truth, predicted, labels=[0, 1], zero_division=0)
    return {
        "accuracy": float(accuracy_score(truth, predicted)),
        "macro_f1": float(np.mean(f1)),
        "confusion_matrix": confusion_matrix(truth, predicted, labels=[0, 1]).tolist(),
        "classes": {
            label: {
                "precision": float(precision[i]),
                "recall": float(recall[i]),
                "f1": float(f1[i]),
                "support": int(support[i]),
                "predicted_count": int(np.sum(predicted == i)),
            }
            for i, label in enumerate(CLASSES)
        },
        "zero_division": 0,
    }


def experiment(records, approved):
    """Fit preprocessing on DPR/RAG only; no tuning or held-out feature selection."""
    by_id = {r["chunk_id"]: r for r in records}
    train = [r for r in approved if r["paper_id"] in TRAIN_PAPERS]
    test = [r for r in approved if r["paper_id"] == TEST_PAPER]
    require(
        len(train) == 10 and len(test) == 5 and {r["chunk_id"] for r in train}.isdisjoint(r["chunk_id"] for r in test),
        "Unexpected paper-disjoint split",
    )

    def matrix(rows):
        return np.array([[by_id[r["chunk_id"]]["features"][f] for f in FEATURES] for r in rows], dtype=float)

    x_train, x_test = matrix(train), matrix(test)
    require(np.isfinite(x_train).all() and np.isfinite(x_test).all(), "Nonfinite graph features")
    require(np.any(np.var(x_train[:, :6], axis=0) > 0), "No informative training graph variation")
    y_train = np.array([CLASSES.index(r["label"]) for r in train])
    y_test = np.array([CLASSES.index(r["label"]) for r in test])
    require(set(y_train) == set(y_test) == {0, 1}, "Both classes required in each partition")
    model = make_pipeline(
        StandardScaler(), LogisticRegression(**{k: v for k, v in SETTINGS.items() if k != "threshold"})
    )
    estimators = {"majority": DummyClassifier(strategy="most_frequent"), "logistic": model}
    report = {
        "settings": SETTINGS,
        "feature_order": FEATURES,
        "train": train,
        "test": test,
        "train_variance": np.var(x_train, axis=0).tolist(),
        "test_variance": np.var(x_test, axis=0).tolist(),
        "train_mean": np.mean(x_train, axis=0).tolist(),
        "results": {},
    }
    for name, estimator in estimators.items():
        started = time.perf_counter()
        estimator.fit(x_train, y_train)
        fit_seconds = time.perf_counter() - started
        started = time.perf_counter()
        probability = estimator.predict_proba(x_test)[:, 1]
        prediction = (probability >= SETTINGS["threshold"]).astype(int)
        elapsed = time.perf_counter() - started
        report["results"][name] = {
            "metrics": metrics(y_test, prediction),
            "training_seconds": fit_seconds,
            "inference_seconds": elapsed,
            "predictions": [
                {
                    "chunk_id": r["chunk_id"],
                    "predicted": CLASSES[int(v)],
                    "evaluation_probability": float(p),
                    "status": "HYPOTHESIS",
                }
                for r, v, p in zip(test, prediction, probability)
            ],
        }
    report["scaler_mean"] = model.named_steps["standardscaler"].mean_.tolist()
    return model, report
