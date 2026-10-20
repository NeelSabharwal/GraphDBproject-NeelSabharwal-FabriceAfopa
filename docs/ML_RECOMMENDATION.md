# ML recommendation for October 23

**Recommend a small supervised Method-versus-Evaluation classifier on existing Chunk nodes. Do not rely on citation-link prediction for this deadline.** This is a recommendation, not an architecture change, implemented model or verified grading result. No labels, trained model or performance measurements were created in this task.

## Decision against the professor's requirement

The professor's specification says an ML workflow may predict links **or classify nodes**; the checklist allocates three points to an ML prediction/classification workflow. A trained classifier with graph-derived features, a genuine held-out split, baseline and measured results is a concrete way to address that requirement. PageRank, a keyword rule, or relabeling an LLM's guesses would not constitute this supervised experiment. The separate requirement for a GDS projection and at least two algorithms still remains.

| Consideration | Citation-link prediction | Chunk-node classification |
| --- | --- | --- |
| Current labels | 13 checked positive references; no complete verified negative-label audit | No labels yet; students can label bounded prose directly |
| Size | 10 papers, 90 possible ordered non-self pairs; these are not 90 labels | More candidate nodes per paper; exact usable count awaits ingestion |
| Main work | Complete bibliography audit, identity resolution, negative-label policy, edge-removal features | Review prose labels, export local graph features, fit one small model |
| Independence | Many pairs share the same ten endpoints | Chunks are dependent too; split by whole paper |
| Deadline judgment | Computable as a toy demo, but not a defensible main plan under the current evidence/gate | More manageable, conditional on ingestion and student annotation |

A 60/20/20 split of 13 positives leaves only about 8/2/3 positives. The project's provisional 50-positive gate is unmet; it is not a professor rule. With an additional strict earlier-first-submission eligibility rule, ten papers would have at most 45 candidate pairs, already below that gate; this is an illustrative bound, **not a rule silently added to the existing design**. Without that rule the bound is 90, but nothing verifies 50 actual citations. Do not expand the corpus or lower the gate simply to manufacture feasibility. Keep the 13 links for graph-path demonstrations. A missing CSV row remains unknown, not negative.

## Smallest proposed experiment

Use **eight papers from the existing ten**, avoiding known ColBERT and G-Retriever extraction issues for the first ML run. No new papers or services are needed. Proposed fixed split, to freeze before model fitting:

| Partition | Pinned v1 paper IDs | Purpose |
| --- | --- | --- |
| Train: 6 papers | 2004.04906 (DPR), 2005.11401 (RAG), 2002.08909 (REALM), 2007.01282 (FiD), 2310.11511 (Self-RAG), 2410.05779 (LightRAG) | Fit preprocessing and classifier |
| Test: 2 papers | 2404.16130 (GraphRAG), 2405.14831 (HippoRAG) | Evaluate transfer to unseen papers |

Target **12 unambiguous chunks per paper: 6 Method and 6 Evaluation**, giving a proposed 96 labels (72 train, 24 test). These are targets, not existing dataset statistics. This balanced, purposive sample measures the selected two-class task, not natural corpus prevalence. If the actual chunking cannot supply these examples, record the shortfall and reduce scope transparently before fitting; do not fabricate or duplicate samples. Require both classes in train and test and at least four examples of each class in each test paper for the minimum proposed demonstration. Even then, two held-out papers give limited generalization evidence.

No hyperparameter search is needed, so no validation split is needed for this minimal experiment. Fix preprocessing, model settings and a 0.5 decision threshold before opening test results. Test-set quality or class-availability checks may reject unusable data before fitting; test performance must never determine exclusions or replacements.

## Labeling protocol

1. Use the actual ingestion-generated Chunk IDs, paper/version hashes, pages and offsets. Do not create a competing chunker for ML. Freeze the chunking version. Inspect text quality for all eight selected papers, including LightRAG; a PDF yielding text is not enough.
2. **Method:** the chunk's main purpose explains the authors' proposed system, algorithm or training objective. **Evaluation:** it explains empirical test setup, datasets, baselines, measurement or results. Training objectives are Method; dataset preparation for an experiment is Evaluation. Abstracts, related work, references, captions-only/table-only chunks, mixed-purpose chunks and unreadable text are **EXCLUDE**, with a reason, not a third prediction class.
3. Review eligible chunks in stable `(paper_id, page, ordinal)` order. Label until each class quota is met; record candidates examined and exclusions. Do not choose examples based on model predictions or graph feature values. If overlapping chunks repeat substantially the same passage, retain one to limit pseudo-replication. Splitting whole papers already prevents their overlap from crossing partitions.
4. A student reads the source and records label, rationale, reviewer and timestamp. A second student independently labels **all proposed test examples** and a fixed 20% of training examples, blind to the first label. Report raw agreement and resolve disagreements before release. If only one student is available, disclose single-review annotation rather than inventing a reviewer.
5. Save a label table with `chunk_id, paper_id, pdf_sha256, page, start, end, label, exclusion_reason, reviewer, reviewed_at, second_label, adjudication, split`. Keep test labels in evaluation-only storage, outside prompts, retrieval, graph properties and training feature exports.

## Graph-derived features and leakage controls

Use the existing MENTIONS and NEXT relationships through an adapter to the actual repository schema. For chunk c, let E(c) be the set of distinct mentioned entity IDs after the fixed resolution policy. Use:

- Four counts: distinct neighbors of kinds Method, Dataset, Task and Topic. Apply log(1+x); count each entity once. Unknown kinds are excluded and their frequency is reported as a quality diagnostic.
- Jaccard overlap of E(c) with E(previous chunk) and E(next chunk) **within the same paper**: intersection size / union size. Use zero for an empty union.
- Two flags indicating whether those previous/next neighbors exist, distinguishing a missing neighbor from zero overlap.

These eight numeric features encode typed local graph neighborhoods. A standard supervised [logistic regression](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html) is trained on these features; the experiment need not train a GNN or use a GDS ML pipeline. Standardize using training-set means/scales only; use L2 regularization, fixed C=1, threshold 0.5 and seed 42. Save exact library versions and solver settings actually used. Compare with a [training-majority classifier](https://scikit-learn.org/stable/modules/generated/sklearn.dummy.DummyClassifier.html) using `most_frequent`. If the training features are all constant or MENTIONS is missing, stop and report the blocker; do not report a graph-based model trained on paper IDs or text position instead.

Exclude headings/section labels, paper IDs, page position, literal section-role indicators, LLM chunk-role predictions, evaluation gold answers, Claim status created from these annotations, and any feature derived from the target label. Entity kinds such as Method describe mentioned entities, not the supervised role of the chunk. Run the same label-blind entity extraction/alias rules on every paper; do not manually improve test extraction using the labels. Filter heading-only mentions from the feature export using source spans and a declared uniform rule; if provenance cannot distinguish them, record that limitation before fitting. Follow the [training-only preprocessing guidance](https://scikit-learn.org/stable/common_pitfalls.html); never fit preprocessing on the test partition.

Compute feature neighborhoods per paper. Do not propagate through shared entities into training/test papers, use corpus-wide degrees/PageRank or learn embeddings on all papers. Label-free features from a held-out document's own graph are allowed: they are information available when classifying a new document. Labels for neighboring chunks must never be used. Duplicate/alternate versions of a work stay in the same partition. Do not feed this classifier's predictions back into the evaluation graph.

## Evidence to deliver, not results to assume

Report actual label/exclusion counts by paper and class; reviewer agreement; training feature variance; train/test paper IDs; majority baseline and model **macro-F1**, per-class precision/recall and confusion matrix. Macro-F1 is the unweighted mean of the two class F1 scores; fix the label list to Method and Evaluation and set zero-division behavior to zero, reporting undefined cases explicitly ([metric definition](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.f1_score.html)). Report per-test-paper results as well as pooled results, with supports. Accuracy is secondary. Do not calculate chunk-level confidence intervals pretending chunks are independent; explicitly state the limitation of only two test papers.

Retain the frozen split, features, preprocessing, model artifact, predictions, exact commands, seed and metrics. Beating the baseline is not guaranteed and is not a reason to relabel test examples. Honest weak performance can still demonstrate the workflow, provided the student explains it and the professor accepts the implementation.

## Deadline sequence and open gates

- **Oct 20:** agree the experiment; finish prototype ingestion and verify the feature inputs. No automatic architecture edit is authorized by this recommendation.
- **Oct 21:** ingest the five additional selected papers, annotate and adjudicate; freeze labels and split.
- **Oct 22:** fit baseline and classifier once; evaluate, preserve failures and write the report.
- **Oct 23:** reproduce the run and prepare the defense. Avoid late corpus expansion.

Repository schema, actual chunk counts, entity quality, annotation availability and runtime remain unverified here. If eight-paper ingestion/labels are not ready, report the ML criterion as incomplete rather than replacing a held-out experiment with a three-paper training-set score.
