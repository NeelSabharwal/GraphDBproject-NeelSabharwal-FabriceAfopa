"""Synthetic leakage and metric checks, not research-corpus performance claims."""

from copy import deepcopy
import numpy as np
import pytest

from app.ml.features import FEATURES, extract_features, jaccard
from app.ml.pilot import CLASSES, TEST_PAPER, TRAIN_PAPERS, experiment, metrics
from app.ml.pilot import labels as validated_labels
from app.mentions.graph import properties
from app.mentions.matcher import generate, rules
from test_mentions import mention_source  # noqa: F401


def feature_fixture(source):
    """Two local neighbors; repeated occurrences count once by entity identity."""
    first = next(iter(source["chunks"].values()))
    second = dict(first, id=first["id"] + "next")
    paper = dict(id=first["paper_id"], pdf_sha256=first["pdf_sha256"])
    rows = [r for r in generate(source, rules()) if r["decision"] == "PROPOSED"]
    entity = source["entities"][rows[0]["entity_id"]]
    nodes = [
        dict(identity=p["id"], labels=[label], properties=p)
        for p, label in [(first, "Chunk"), (second, "Chunk"), (paper, "Paper"), (entity, "Entity")]
    ]
    edges = [dict(source=c["id"], target=paper["id"], type="PART_OF", properties={}) for c in (first, second)]
    edges.append(dict(source=first["id"], target=second["id"], type="NEXT", properties={}))
    edges += [
        dict(source=c["id"], target=entity["id"], type="MENTIONS", properties=properties(row))
        for c in (first, second)
        for row in rows
    ]
    return dict(nodes=nodes, relationships=edges)


def test_real_relationship_features_deduplicate_occurrences(mention_source):
    state = feature_fixture(mention_source)
    result = extract_features(state)
    assert result[0]["features"]["mentions_method_log1p"] == pytest.approx(np.log(2))
    assert result[0]["features"]["jaccard_next"] == 1
    assert result[1]["features"]["jaccard_previous"] == 1
    assert result[0]["features"]["has_previous"] == 0
    assert result[1]["features"]["has_next"] == 0
    assert set(result[0]["features"]) == set(FEATURES)


@pytest.mark.parametrize("fault", ["cross-paper", "hash", "span", "policy", "ambiguous"])
def test_invalid_graph_features_fail_closed(mention_source, fault):
    state = feature_fixture(mention_source)
    if fault == "cross-paper":
        state["nodes"][1]["properties"]["paper_id"] = "different"
    elif fault == "hash":
        state["nodes"][0]["properties"]["text_sha256"] = "changed"
    elif fault == "span":
        state["relationships"][-1]["properties"]["surface"] = "forged"
    elif fault == "policy":
        state["relationships"][-1]["properties"]["policy_sha256"] = "changed"
    else:
        state["relationships"].append(
            dict(source=state["nodes"][0]["identity"], target=state["nodes"][0]["identity"], type="NEXT", properties={})
        )
    with pytest.raises(ValueError):
        extract_features(state)


@pytest.mark.parametrize("fault", [None, "hash", "reviewer", "approval", "eligibility", "duplicate", "label"])
def test_approved_label_gate_uses_source_and_independent_review(tmp_path, fault):
    import csv
    from pathlib import Path

    with Path("data/ml/chunk_label_candidates.csv").open(newline="") as stream:
        rows = list(csv.DictReader(stream))
    records = [
        dict(
            chunk_id=r["chunk_id"],
            paper_id=r["paper_id"],
            pdf_sha256=r["pdf_sha256"],
            text_sha256=r["mapped_chunk_text_sha256"],
        )
        for r in rows
        if r["training_eligibility"] == "ELIGIBLE_REVIEWED_PILOT"
    ]
    row = next(r for r in rows if r["candidate_id"] == "ML01")
    fields = {
        "hash": "mapped_chunk_text_sha256",
        "reviewer": "independent_reviewer",
        "approval": "whole_chunk_approval",
        "eligibility": "training_eligibility",
        "label": "approved_whole_chunk_label",
    }
    if fault in fields:
        row[fields[fault]] = "tampered"
    if fault == "duplicate":
        rows[-1]["candidate_id"] = "ML01"
    path = tmp_path / "labels.csv"
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    if fault:
        with pytest.raises(ValueError):
            validated_labels(path, records)
    else:
        assert len(validated_labels(path, records)) == 15


def synthetic_pilot():
    records = []
    approved = []
    for paper in (*TRAIN_PAPERS, TEST_PAPER):
        for i in range(5):
            ident = f"synthetic:{paper}:{i}"
            values = [float(i % 3), float(i % 2), float(i == 2), 0.0, 0.0, 0.0, 1.0, 1.0]
            records.append(dict(chunk_id=ident, paper_id=paper, features=dict(zip(FEATURES, values))))
            approved.append(dict(chunk_id=ident, paper_id=paper, label=CLASSES[int(i >= 2)], candidate_id=ident))
    return records, approved


def test_training_is_deterministic_and_paper_disjoint():
    records, approved = synthetic_pilot()
    model, report = experiment(records, approved)
    again, repeated = experiment(records, approved)
    np.testing.assert_array_equal(
        model.named_steps["logisticregression"].coef_, again.named_steps["logisticregression"].coef_
    )
    assert report["results"]["logistic"]["metrics"] == repeated["results"]["logistic"]["metrics"]
    assert {r["paper_id"] for r in report["train"]} == set(TRAIN_PAPERS)
    assert {r["paper_id"] for r in report["test"]} == {TEST_PAPER}


def test_held_out_values_and_labels_cannot_change_fitted_model():
    records, approved = synthetic_pilot()
    model, report = experiment(records, approved)
    changed = deepcopy(records)
    for r in changed:
        if r["paper_id"] == TEST_PAPER:
            r["features"]["mentions_method_log1p"] = 10000.0
    labels = deepcopy(approved)
    for r in labels:
        if r["paper_id"] == TEST_PAPER:
            r["label"] = CLASSES[1 - CLASSES.index(r["label"])]
    other, after = experiment(changed, labels)
    np.testing.assert_array_equal(
        model.named_steps["logisticregression"].coef_, other.named_steps["logisticregression"].coef_
    )
    assert report["scaler_mean"] == after["scaler_mean"] == report["train_mean"]


def test_constant_graph_features_fail_instead_of_training_on_flags():
    records, approved = synthetic_pilot()
    for r in records:
        r["features"] = dict(zip(FEATURES, [0, 0, 0, 0, 0, 0, 1, 1]))
    with pytest.raises(ValueError, match="variation"):
        experiment(records, approved)


def test_unknown_paper_cannot_enter_training():
    records, approved = synthetic_pilot()
    approved[0]["paper_id"] = "unapproved-paper"
    with pytest.raises(ValueError, match="split"):
        experiment(records, approved)


def test_metrics_include_missing_predictions_and_fixed_class_order():
    result = metrics(np.array([0, 0, 1, 1, 1]), np.ones(5, dtype=int))
    assert result["accuracy"] == 0.6
    assert result["macro_f1"] == pytest.approx(0.375)
    assert result["confusion_matrix"] == [[0, 2], [0, 3]]
    assert result["classes"]["METHOD"]["precision"] == 0
    assert result["classes"]["METHOD"]["support"] == 2


def test_empty_and_distinct_neighbor_jaccard():
    assert jaccard(set(), set()) == 0
    assert jaccard({"a", "b"}, {"b", "c"}) == pytest.approx(1 / 3)


def test_empty_graph_cannot_invent_features():
    assert extract_features(dict(nodes=[], relationships=[])) == []
