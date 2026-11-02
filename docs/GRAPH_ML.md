# Graph-derived Chunk classification — executed educational pilot

**Executed 2026-11-02.** The fixed classifier ran successfully but did **not** predict
any of the five held-out labels correctly. This failed generalization result is
retained; no held-out tuning, relabeling or feature selection was performed.

## Eligibility, split and features

The original annotation CSV is unchanged. All 15 approved Chunk IDs, text/PDF hashes,
Paper memberships and explicit NeelSabharwal whole-Chunk approval fields dated
2026-10-22 passed validation. ML02/10/17 remain unresolved; ML07/14/21 remain excluded.
Every paper contributes two METHOD and three EVALUATION Chunks. DPR+RAG provide ten
training examples; GraphRAG provides five held-out examples. The labels remain
historically `DEVELOPMENT_ONLY`: this is not a newly blinded test set.

The fixed eight inputs in `app/ml/features.py` are four log(1+distinct entity count)
features (Method, Dataset, Task, Topic), previous/next entity-set Jaccard similarities,
and previous/next existence flags. Only the controlled v4 MENTIONS batch with
accepted canonical identities contributes; the three legacy unreviewed mentions do
not. NEXT must be an actual same-paper relationship. Repeated occurrences count
once per entity. Empty-set Jaccard is zero. No paper ID, page, text, heading, label,
review decision, global degree or prediction enters the feature matrix. IDs/hashes
are metadata used to validate the split, not learner inputs.

Actual source graph: DPR 42 Chunks / 23 with controlled mentions; RAG 62 / 16;
GraphRAG 49 / 13. The 15 approved examples have **10 distinct feature vectors**.
Ten of those examples contain a controlled mention; the frozen proposal has 55
occurrences on these ten examples. All 153 Chunks use the same source-matching rules.

| Feature | Pilot minimum | Maximum | Mean | Zero values / 15 |
|---|---:|---:|---:|---:|
| Method log-count | 0 | 1.386294 | 0.323469 | 9 |
| Dataset log-count | 0 | 1.609438 | 0.518882 | 9 |
| Task log-count | 0 | 0.693147 | 0.231049 | 10 |
| Topic log-count | 0 | 0 | 0 | 15 |
| Previous Jaccard | 0 | 0.5 | 0.063333 | 12 |
| Next Jaccard | 0 | 0.8 | 0.21 | 8 |
| Has previous | 1 | 1 | 1 | 0 |
| Has next | 1 | 1 | 1 | 0 |

Training variances in feature order:
`[0.211399, 0.505603, 0.115309, 0, 0.008225, 0.070025, 0, 0]`.
The three constant features are retained as predeclared; they were not removed based
on test performance. Graph variation exists beyond position flags, but the indicators
are sparse and strongly tied to the small approved named-entity vocabulary.

## Frozen experiment and measured results

Python **3.12.13**, scikit-learn **1.7.2**. Logistic regression: L2, C=1, liblinear,
seed=42, max_iter=1000, threshold=0.5, StandardScaler fitted only on DPR+RAG. Settings
were saved before opening performance results. Baseline: training most-frequent class.
Class order for matrices is `[METHOD, EVALUATION]`; rows are truth, columns prediction.
Undefined class metrics use zero and retain their supports.

| Model | Accuracy | Macro-F1 | Confusion matrix | Fit seconds | Predict seconds |
|---|---:|---:|---|---:|---:|
| Majority (EVALUATION) | 0.60 | 0.375 | `[[0,2],[0,3]]` | 0.000395 | 0.000041 |
| Graph-feature logistic | 0.00 | 0.000 | `[[0,2],[3,0]]` | 0.001060 | 0.000241 |

| Model / class | Precision | Recall | F1 | Support |
|---|---:|---:|---:|---:|
| Majority / METHOD | 0 | 0 | 0 | 2 |
| Majority / EVALUATION | 0.60 | 1 | 0.75 | 3 |
| Logistic / METHOD | 0 | 0 | 0 | 2 |
| Logistic / EVALUATION | 0 | 0 | 0 | 3 |

Times measure estimator fit/predict only, not PDF validation or graph export. No
non-overlap diagnostic or alternate model was selected after seeing these results.
Model and predictions remain ignored artifacts and hypotheses, never Neo4j facts.
The persisted graph fingerprint was unchanged during the entire experiment.

## Reproduction and tests

The code is `app/ml/{features,pilot}.py` and `scripts/train_graph_ml.py`. After an
already verified/enriched source graph, run once into a new directory:

```bash
docker compose run --rm --no-deps -T --user "$(id -u):$(id -g)" \
  -v "$PWD:/workspace:ro" -v "$PWD/data:/workspace/data:ro" \
  -v "$PWD/data/processed:/workspace/data/processed" \
  --entrypoint python api -m scripts.train_graph_ml \
  --output data/processed/ml/reproduction-01
```

The actual run is `data/processed/final-delivery-20261102/ml-pilot/`: settings,
features for 153 Chunks, full metrics/predictions, `model.joblib`, and checksum.
Never load an untrusted joblib/pickle. Annotation SHA-256:
`301bccb14515daa90bbe67778e77dd8afeaa85e92592e02b42d8286839964b51`.
Tests cover exact eligibility, changed hashes/reviewer/status, distinct Chunk IDs,
local graph features, bad provenance/NEXT, fixed metrics and paper-disjoint splitting.
Changing held-out features or labels cannot change fitted coefficients or scaler.

## Interpretation and unmet target

Three papers, 15 labels and one five-example test paper cannot establish AI-literature
generalization. The labels were development-visible, Chunks overlap, named-entity
coverage is selective, and DPR/RAG versus GraphRAG is a substantial task/domain shift.
That is a plausible limitation, not a proven causal diagnosis of the zero score.
The original **eight-paper / 96-label** target and blinded-review protocol remain
unmet. The professor determines whether this honest educational workflow earns the
ML criterion. Do not claim useful predictive performance or replace the failed result.
