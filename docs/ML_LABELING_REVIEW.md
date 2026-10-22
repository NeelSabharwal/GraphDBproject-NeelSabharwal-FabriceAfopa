# ML labeling review — Method vs Evaluation Chunk classification

**Project:** Project 8 — AI Research GraphRAG Assistant (Level 3+)
**Deadline:** 2026-10-23
**Review type:** preserved AI-assisted passage proposals and technical mappings, with independently human-approved pilot Chunk labels recorded separately below.
**Passage review status:** **APPROVED** by **Fabrice Afopa** on **2026-10-21** for all 21 passage interpretations, including ML07, ML14 and ML21 as `AMBIGUOUS/EXCLUDE`. This approval applies only to the cited passages; it does **not** approve, label, or otherwise certify their containing Neo4j Chunks.
**Independent whole-Chunk review:** **NeelSabharwal**, **2026-10-22**, personally confirmed the proposed labels of the **15 uniquely mapped complete Chunks** for the ML pilot. ML02, ML10 and ML17 remain unresolved; ML07, ML14 and ML21 remain excluded. See Section 10 for the scope and CSV fields.
**Database/ML operations:** **NOT PERFORMED** — no Neo4j writes, training, prediction, evaluation or performance numbers.

## 1. Authority, sources and reproduction

The professor’s [`projects_spec.md`](../docs/requirements/projects_spec.md) (Project 8 and Graph Data Science/Agentic section) and [`project_checklist.md`](../docs/requirements/project_checklist.md) permit a **node-classification ML workflow (3 points)**. This labeling file by itself does not meet that rubric item. The repository’s [`ML_RECOMMENDATION.md`](ML_RECOMMENDATION.md), [`ARCHITECTURE.md`](ARCHITECTURE.md) and [`corpus_manifest.json`](../corpus/corpus_manifest.json) specify the provisional Chunk-labeling and leakage-control design. The recommendation’s 8-paper/96-label target is conditional, not an achieved count.

The original passage proposal used only the three manifest-pinned **v1** PDFs as scientific evidence. Its recorded checks found that local uploaded bytes matched the manifest SHA-256 values and all 21 short excerpts occurred uniquely on the stated PDF pages; it also reported rendered inspection of a sample of relevant pages. **That passage extraction used `pypdf 5.9.0`**, whereas ingestion records `pypdf 6.10.0`. No Chunk IDs or offsets were derived from the older extraction. Section 8 subsequently mapped passages against the authentic Chunk export; stored IDs, offsets and hashes in the CSV come from that export. This reconciliation does not claim a new PDF inspection or live database audit.

| Paper | Exact pinned PDF | Pages | Manifest SHA-256 |
|---|---|---:|---|
| DPR | [arxiv:2004.04906v1](https://arxiv.org/pdf/2004.04906v1) | 10 | `2b03fbde33c88fcf82091e6325806bd2656ca777032471e182c602c76ccdab01` |
| RAG | [arxiv:2005.11401v1](https://arxiv.org/pdf/2005.11401v1) | 18 | `25b55fd0f7c6c91cbe2c88690a33923077103e8f563d154faa1ce11d3527e601` |
| GraphRAG | [arxiv:2404.16130v1](https://arxiv.org/pdf/2404.16130v1) | 15 | `33524b3b56910c513affdad8dbf67d14e68edf0572e4debdb09a9f1916463b06` |

## 2. Concise annotation rubric

| Proposed decision | Whole-Chunk rule | Examples and traps |
|---|---|---|
| `METHOD` | The **main purpose of the entire stored Chunk** is to describe the authors’ system, architecture, algorithm, training objective or procedural mechanism. | Retriever/encoder architecture, RAG-Sequence mathematics, Leiden community detection, map-reduce answering. Training **objective** = METHOD. |
| `EVALUATION` | The main purpose is experimental data/setup, benchmarks, comparison conditions, metrics, measured outcomes or analysis of results. | QA benchmark selection, exact-match evaluations, human judgments, corpus configuration. Experimental training **hyperparameters** or dataset preparation = EVALUATION, when part of an experiment. |
| `AMBIGUOUS/EXCLUDE` | Chunk combines both roles substantially, is only an abstract/related-work/reference/header/caption/table, is unreadable, or lacks enough context. **Exclude**, never coerce into a binary class. | A page crossing method-to-experiment sections or a dataset mentioned in related work is not automatically an evaluation example. |

**Decision rule:** Open the mapped Chunk’s *complete normalized text*, then its original PDF page and surrounding context; decide its dominant communicative role. The short excerpt is only a locator. If one excerpt lies in several overlapping Chunks, choose at most one eligible, distinct Chunk after manual review. If a Chunk crosses role boundaries or consists chiefly of heading/caption/table fragments, exclude it and record why. Do not label using section title, page number or model prediction alone.

## 3. Candidate evidence table

The companion CSV is [`data/ml/chunk_label_candidates.csv`](../data/ml/chunk_label_candidates.csv). **Proposed counts: 9 METHOD, 9 EVALUATION and 3 exclusion controls** (21 locators). These are *passages*, not 18 unique mapped/eligible Neo4j Chunks or a guaranteed balanced dataset. The CSV retains exact text including PDF-extraction line breaks and typographic artifacts.

| ID | Paper / PDF page / section | Proposed label | Scientific justification / uncertainty |
|---|---|---|---|
| `ML01` | DPR p.3, 3.1 Overview | `METHOD` | Explains the model’s passage encoder and retrieval architecture. |
| `ML02` | DPR p.3, 3.1 Encoders | `METHOD` | Specifies two distinct BERT encoders and representation choice. |
| `ML03` | DPR p.4, 3.2 Training (continuation) | `METHOD` | Defines in-batch negatives and the training procedure. |
| `ML04` | DPR p.4, 4.2 Question Answering Datasets | `EVALUATION` | Describes datasets and experiment splits rather than a retrieval algorithm. |
| `ML05` | DPR p.5, 5.1 Main Results | `EVALUATION` | Introduces comparative empirical retrieval results and evaluation metric. |
| `ML06` | DPR p.8, 6.2 Results | `EVALUATION` | Reports the final empirical QA evaluation and exact-match metric. |
| `ML07` | DPR p.1, Abstract | `AMBIGUOUS/EXCLUDE` | Abstract interleaves motivation, method claims, and evaluation outcomes; exclude from binary model. |
| `ML08` | RAG p.3, 2.1 Models | `METHOD` | Defines RAG-Sequence latent-document mechanism. |
| `ML09` | RAG p.3, 2.2 Retriever: DPR | `METHOD` | Describes the retriever implementation and model components. |
| `ML10` | RAG p.3, 2.3 Generator: BART | `METHOD` | Describes BART-large as the generator model. |
| `ML11` | RAG p.4, 3.1 Open-domain Question Answering | `EVALUATION` | Defines the benchmark datasets used in the QA experiments. |
| `ML12` | RAG p.6, 4.1 Open-domain Question Answering | `EVALUATION` | Compares experimental test scores against baselines. |
| `ML13` | RAG p.7, 4.3 Jeopardy Question Generation | `EVALUATION` | Reports comparative human judgments and experimental findings. |
| `ML14` | RAG p.1, Abstract | `AMBIGUOUS/EXCLUDE` | Abstract mixes a method introduction and experimental performance claims. |
| `ML15` | GraphRAG p.3, 2.2 Text Chunks → Element Instances | `METHOD` | Specifies the paper’s entity/relationship extraction workflow. |
| `ML16` | GraphRAG p.4, 2.4 Element Summaries → Graph Communities | `METHOD` | Explains selected graph community detection algorithm. |
| `ML17` | GraphRAG p.5, 2.6 Community Summaries → Community Answers → Global Answer | `METHOD` | Describes the map-stage generation of the method. |
| `ML18` | GraphRAG p.6, 3.1 Datasets | `EVALUATION` | Defines corpora selected for performance assessment. |
| `ML19` | GraphRAG p.7, 3.4 Metrics | `EVALUATION` | Describes measures and evaluator protocol for experiments. |
| `ML20` | GraphRAG p.9, 3.6 Results | `EVALUATION` | Quantifies experimental graph/index outcome in the results section. |
| `ML21` | GraphRAG p.6, 3.2 Queries | `AMBIGUOUS/EXCLUDE` | Benchmark names here are background comparison, not proof they were used for the main experiment. |

### Mapping and approval gates

The original proposal left Chunk identifiers and review fields empty. Sections 8–10 supersede that initial state: 15 distinct selected Chunks now have stored IDs, offsets/hashes and NeelSabharwal's independent whole-Chunk approval. The three overlapping mappings retain no selected `chunk_id`; exclusions retain their technical references in `supporting_chunk_ids`. All rows remain `proposed_split=DEVELOPMENT_ONLY`; adjudication and blinded second-label fields remain empty because no such exercise was reported. **Never derive an alleged real Chunk ID from these page excerpts.** The eventual trained unit is the **existing** Neo4j `Chunk`, not an invented passage ID.

For further candidates: locate each excerpt in the exact `Paper` version's linked `Chunk` texts, record real Chunk ID and **stored** page offsets/hash, verify `PART_OF`, original PDF hash and overlap, and examine the *whole* Chunk. Two source passages may map to one Chunk; count it once or exclude if mixed. Record exclusions and every candidate examined. Record the student's actual identity, supplied date and decision without inventing a time of day; this document must not trigger database Claim approval.

### Historical initial mapping attempt — 2026-10-21, before export mapping

The initial review session reported no local Neo4j access (`.env` absent and Docker API inaccessible), so it attempted no database query or write and inferred no Chunk IDs or offsets. The following table preserves that initial review queue only. **It is historical, not the current mapping or approval state**; Section 8 records the later export mapping and Section 10 the current independent approvals.

| Candidate | Source / page | Declared passage interpretation | Actual Chunk ID | Proposed whole-Chunk decision | Overlap / duplicate warning | Whole-Chunk approval |
|---|---|---|---|---|---|---|
| ML01 | DPR p.3 | METHOD | Unmapped | Pending live-Chunk inspection | Not assessed | Pending |
| ML02 | DPR p.3 | METHOD | Unmapped | Pending live-Chunk inspection | Not assessed | Pending |
| ML03 | DPR p.4 | METHOD | Unmapped | Pending live-Chunk inspection | Not assessed | Pending |
| ML04 | DPR p.4 | EVALUATION | Unmapped | Pending live-Chunk inspection | Not assessed | Pending |
| ML05 | DPR p.5 | EVALUATION | Unmapped | Pending live-Chunk inspection | Not assessed | Pending |
| ML06 | DPR p.8 | EVALUATION | Unmapped | Pending live-Chunk inspection | Not assessed | Pending |
| ML07 | DPR p.1 | AMBIGUOUS/EXCLUDE | Unmapped | Proposed exclusion pending live-Chunk inspection | Not assessed | Pending |
| ML08 | RAG p.3 | METHOD | Unmapped | Pending live-Chunk inspection | Not assessed | Pending |
| ML09 | RAG p.3 | METHOD | Unmapped | Pending live-Chunk inspection | Not assessed | Pending |
| ML10 | RAG p.3 | METHOD | Unmapped | Pending live-Chunk inspection | Not assessed | Pending |
| ML11 | RAG p.4 | EVALUATION | Unmapped | Pending live-Chunk inspection | Not assessed | Pending |
| ML12 | RAG p.6 | EVALUATION | Unmapped | Pending live-Chunk inspection | Not assessed | Pending |
| ML13 | RAG p.7 | EVALUATION | Unmapped | Pending live-Chunk inspection | Not assessed | Pending |
| ML14 | RAG p.1 | AMBIGUOUS/EXCLUDE | Unmapped | Proposed exclusion pending live-Chunk inspection | Not assessed | Pending |
| ML15 | GraphRAG p.3 | METHOD | Unmapped | Pending live-Chunk inspection | Not assessed | Pending |
| ML16 | GraphRAG p.4 | METHOD | Unmapped | Pending live-Chunk inspection | Not assessed | Pending |
| ML17 | GraphRAG p.5 | METHOD | Unmapped | Pending live-Chunk inspection | Not assessed | Pending |
| ML18 | GraphRAG p.6 | EVALUATION | Unmapped | Pending live-Chunk inspection | Not assessed | Pending |
| ML19 | GraphRAG p.7 | EVALUATION | Unmapped | Pending live-Chunk inspection | Not assessed | Pending |
| ML20 | GraphRAG p.9 | EVALUATION | Unmapped | Pending live-Chunk inspection | Not assessed | Pending |
| ML21 | GraphRAG p.6 | AMBIGUOUS/EXCLUDE | Unmapped | Proposed exclusion pending live-Chunk inspection | Not assessed | Pending |

Complete stored Chunk texts were unavailable in that initial session. They were subsequently supplied through the export in Section 8. The original passage locators remain in the CSV and Section 7; they are not substitutes for full Chunk text.

### Current reviewed pilot counts — 2026-10-22

| Paper | Approved METHOD Chunks | Approved EVALUATION Chunks | Unresolved overlapping candidates | Excluded candidates |
|---|---:|---:|---:|---:|
| DPR | 2 | 3 | 1 (ML02) | 1 (ML07) |
| RAG | 2 | 3 | 1 (ML10) | 1 (ML14) |
| GraphRAG | 2 | 3 | 1 (ML17) | 1 (ML21) |
| **Total** | **6** | **9** | **3** | **3** |

There are now **15 distinct human-approved pilot Chunks**, not 18 binary passage labels. Original passage counts remain 9 METHOD / 9 EVALUATION / 3 exclusions; the reviewed Chunk counts are 6 METHOD / 9 EVALUATION. No class balance was manufactured. Label readiness alone does not satisfy the feature, partition or evaluation gates; the eight-paper proposal remains incomplete and no training is performed here.

## 4. Feasibility and realistic target

**Original deliverable:** map 18 potentially binary-eligible passage proposals, preserving three exclusions. **Current outcome:** 15 distinct approved pilot Chunks, three unresolved overlapping candidates and three excluded candidates. Further mapping or annotation needs its own review; do not backfill a quota or claim that 18 usable labels exist.

**Only three papers are currently imported according to the reviewed project state**, not independently queried in this task. DPR and RAG are related retrieval/QA papers, while GraphRAG has different global-summarization content. A 2-paper-train/1-paper-test experiment would have only one independent held-out paper, with possible class and extraction imbalances. It is suitable, at most, for a **sanity-check demonstration**, not strong generalization or an independently defensible final ML score. Split by whole paper, not random Chunks; overlapping snippets within papers are highly dependent.

The provisional project design specifies **eight papers** (six training: DPR, RAG, REALM, FiD, Self-RAG, LightRAG; two held-out: GraphRAG, HippoRAG) and a conditional 12 eligible Chunks per paper. That remains a future plan requiring source-quality checks, ingestion, genuine annotation and nonconstant graph features. Do **not** claim this CSV achieves its target or rebrand the exposed pilot proposals as an unseen benchmark. If eight-paper ingestion or graph features cannot be completed, document the ML criterion as incomplete.

## 5. Proposed evaluation procedure (not executed)

1. **Freeze snapshot and review labels.** Resolve exact Chunk IDs; check page/hash/text and whole-Chunk eligibility. One student labels every proposed example. A second independently reviews all eventual test cases plus a predeclared 20% of training cases while blinded to the first decision; log raw agreement, conflicts and adjudication. If independence is impossible, disclose that limitation.
2. **Freeze whole-paper partitions before modeling.** Prefer the eight-paper split above if implemented. Keep alternate versions of the same work in one partition. Reject/mark ambiguous inputs before fitting, not after seeing test performance. Preserve all excluded IDs and reasons. This shared candidate CSV is not itself a hidden test set.
3. **Use genuine graph-based inputs.** For each Chunk, derive four **distinct `MENTIONS` entity-neighbor counts** (Method, Dataset, Task, Topic), Jaccard entity overlap with `NEXT` predecessor and successor *within the same paper*, and two neighbor-exists flags. Exactly these eight planned features are label-blind. Missing or constant `MENTIONS`/features block a meaningful graph-feature training claim.
4. **Avoid leakage.** Exclude headings/section-role words, page/ordinal/paper IDs, human label fields, Claim-review labels, gold QA answers, model predictions, test-derived preprocessing, and cross-paper feature propagation. Fit scaling/any preprocessing on training papers only. Keep held-out labels outside prompts, application retrieval and training feature exports.
5. **Fit and compare only after eligibility gates.** Predeclare a training-majority baseline and a single L2 logistic regression (proposed `C=1`, seed 42, decision threshold 0.5); no test-set tuning. Report a confusion matrix, macro-F1, precision/recall/support per class and per held-out paper, exact commands/package versions, feature variance and failures. Do not invent scores or require superiority over baseline.

## 6. Uncertainties and stopping conditions

- `pypdf` parser versions differ; offsets and Chunk membership must be checked against the actual frozen ingestion version, not extrapolated from this pilot.
- The original 21 passage locators and technical mappings are preserved. NeelSabharwal now confirms the labels of 15 complete uniquely mapped Chunks; the other six candidates are not reviewed pilot labels. No additional inspection, blinded annotation exercise or inter-reviewer agreement statistic is asserted.
- The visible prototype previously had very few `MENTIONS` edges; no live graph-feature audit was run for this task. Graph feature sparsity could make the proposed learner infeasible.
- Dataset preparation text and training recipes can mix Method/Evaluation; final decisions require full context and explicit exclusion when no dominant role exists.
- Do not assign GraphRAG to a scored test set using these publicly exposed suggestions without a controlled, frozen annotation/evaluation protocol; all candidates are currently development review material.
- This reconciliation updates only PR #8's review document, annotation CSV and narrow ignore rules, while bringing its branch up to date with `origin/main`. No Python application edits, Neo4j changes, gold-label changes or source-manifest changes are introduced by the reconciliation.

## 7. Original personal-inspection guide and exact passages

Open each linked **pinned PDF page**, read the *entire paragraph and neighboring material*, and compare against the complete stored Chunk before recording a final label. The following code-quoted excerpts were copied from the uploaded PDF extraction and verified to occur on the listed PDF page; line breaks, ligatures and hyphenation remain uncorrected. If the live parser produces a different text layout, reconcile it rather than silently shifting coordinates.

### DPR

**ML01 — PDF page 3, 3.1 Overview — proposed METHOD**: [Open page](https://arxiv.org/pdf/2004.04906v1#page=3)

```text
Our dense passage retriever (DPR) uses a dense
encoder EP (·) which maps any text passage to a d-
dimensional real-valued vectors and build an
```

**ML02 — PDF page 3, 3.1 Encoders — proposed METHOD**: [Open page](https://arxiv.org/pdf/2004.04906v1#page=3)

```text
in this work we use two independent
BERT (Devlin et al., 2019) networks (base, un-
cased) and take the representation at the [CLS]
token as
```

**ML03 — PDF page 4, 3.2 Training (continuation) — proposed METHOD**: [Open page](https://arxiv.org/pdf/2004.04906v1#page=4)

```text
In-batch negatives Assume that we have B
questions in a mini-batch and each one is asso-
ciated with a relevant passage. Let Q and P be the
(B×d) matrix of
```

**ML04 — PDF page 4, 4.2 Question Answering Datasets — proposed EVALUATION**: [Open page](https://arxiv.org/pdf/2004.04906v1#page=4)

```text
We use the same ﬁve QA datasets and train-
ing/dev/testing splitting method as in previous
work (Lee et al., 2019). Below we brieﬂy describe
each dataset
```

**ML05 — PDF page 5, 5.1 Main Results — proposed EVALUATION**: [Open page](https://arxiv.org/pdf/2004.04906v1#page=5)

```text
Table 2 compares different passage retrieval sys-
tems on ﬁve QA datasets, using the top-kaccuracy
(k is 20 or 100). With the exception of
```

**ML06 — PDF page 8, 6.2 Results — proposed EVALUATION**: [Open page](https://arxiv.org/pdf/2004.04906v1#page=8)

```text
Table 5 summarizes our ﬁnal end-to-end QA re-
sults, measured by exact match with the reference
answer after minor normalization as in (Chen et
```

**ML07 — PDF page 1, Abstract — proposed AMBIGUOUS/EXCLUDE**: [Open page](https://arxiv.org/pdf/2004.04906v1#page=1)

```text
Open-domain question answering relies on ef-
ﬁcient passage retrieval to select candidate
contexts, where traditional sparse vector space
models, such as
```

### RAG

**ML08 — PDF page 3, 2.1 Models — proposed METHOD**: [Open page](https://arxiv.org/pdf/2005.11401v1#page=3)

```text
RAG-Sequence Model The RAG-Sequence model uses the same retrieved document to generate
the complete sequence. Technically, it treats the
```

**ML09 — PDF page 3, 2.2 Retriever: DPR — proposed METHOD**: [Open page](https://arxiv.org/pdf/2005.11401v1#page=3)

```text
The retrieval component pη(z|x) is based on DPR [22]. DPR follows a bi-encoder architecture:
pη(z|x) ∝exp ⟨d(z),q(x)⟩
where d(z) is a dense
```

**ML10 — PDF page 3, 2.3 Generator: BART — proposed METHOD**: [Open page](https://arxiv.org/pdf/2005.11401v1#page=3)

```text
The generator component pθ(yi|x,z,y 1:i−1) could be modelled using any encoder-decoder. We use
BART-large [28], a pre-trained seq2seq transformer [ 52] with 400M
```

**ML11 — PDF page 4, 3.1 Open-domain Question Answering — proposed EVALUATION**: [Open page](https://arxiv.org/pdf/2005.11401v1#page=4)

```text
We consider four popular open-domain QA datasets: Natural Questions (NQ) [ 25], TriviaQA
(TQA) [20]. WebQuestions (WQ) [ 3] and CuratedTrec (CT) [ 2].
```

**ML12 — PDF page 6, 4.1 Open-domain Question Answering — proposed EVALUATION**: [Open page](https://arxiv.org/pdf/2005.11401v1#page=6)

```text
Table 1 shows results for RAG along with recent state-of-the-art models. On all four open-domain
QA tasks, RAG sets a new state-of-the-art (in the
```

**ML13 — PDF page 7, 4.3 Jeopardy Question Generation — proposed EVALUATION**: [Open page](https://arxiv.org/pdf/2005.11401v1#page=7)

```text
Table 3 shows the results from the human evaluation. The human evaluation was carried out with
452 pairs of generations from BART and RAG-Token. The annotators indicated that BART was
```

**ML14 — PDF page 1, Abstract — proposed AMBIGUOUS/EXCLUDE**: [Open page](https://arxiv.org/pdf/2005.11401v1#page=1)

```text
Large pre-trained language models have been shown to store factual knowledge
in their parameters, and achieve state-of-the-art results when ﬁne-tuned on
```

### GraphRAG

**ML15 — PDF page 3, 2.2 Text Chunks → Element Instances — proposed METHOD**: [Open page](https://arxiv.org/pdf/2404.16130v1#page=3)

```text
We do this using a multipart LLM prompt that first identifies all
entities in the text, including their name, type, and description, before identifying all
```

**ML16 — PDF page 4, 2.4 Element Summaries → Graph Communities — proposed METHOD**: [Open page](https://arxiv.org/pdf/2404.16130v1#page=4)

```text
In our pipeline, we use Leiden (Traag et al., 2019) on account of
its ability to recover hierarchical community structure of large-scale graphs efficiently
```

**ML17 — PDF page 5, 2.6 Community Summaries → Community Answers → Global Answer — proposed METHOD**: [Open page](https://arxiv.org/pdf/2404.16130v1#page=5)

```text
Map community answers. Generate intermediate answers in parallel, one for each chunk.
The LLM is also asked to generate a score between 0-100 indicating
```

**ML18 — PDF page 6, 3.1 Datasets — proposed EVALUATION**: [Open page](https://arxiv.org/pdf/2404.16130v1#page=6)

```text
We selected two datasets in the one million token range, each equivalent to about 10 novels of text
and representative of the kind of corpora
```

**ML19 — PDF page 7, 3.4 Metrics — proposed EVALUATION**: [Open page](https://arxiv.org/pdf/2404.16130v1#page=7)

```text
We selected three
target metrics capturing qualities that are desirable for sensemaking activities, as well as a control
metric (directness) used as a indicator of
```

**ML20 — PDF page 9, 3.6 Results — proposed EVALUATION**: [Open page](https://arxiv.org/pdf/2404.16130v1#page=9)

```text
The indexing process resulted in a graph consisting of 8564 nodes and 20691 edges for the Podcast
dataset, and a larger graph of 15754 nodes and 19520 edges for the
```

**ML21 — PDF page 6, 3.2 Queries — proposed AMBIGUOUS/EXCLUDE**: [Open page](https://arxiv.org/pdf/2404.16130v1#page=6)

```text
Many benchmark datasets for open-domain question answering exist, including HotPotQA (Yang
et al., 2018), MultiHop-RAG (Tang and Yang, 2024), and
```

**Recorded passage-level approval:** reviewer `Fabrice Afopa`; review date `2026-10-21`; approved passage decisions `ML01–ML21`, including exclusion decisions `ML07`, `ML14`, and `ML21`. That passage-only event did not approve whole Chunks. Subsequent mappings, recommendation acceptance and independent whole-Chunk approval are recorded separately in Sections 8–10.

## 8. Read-only Chunk-export mapping — 2026-10-21

The original mapping review reported finding its supplied export at `data/ml/chunk_export_for_review.json` rather than that task's stated `data/processed/ml/` path. It recorded 153 unique, internally consistent Chunks: 42 DPR, 62 RAG and 49 GraphRAG. Every exported `text_sha256` matched its text; every `end_char - start_char` matched text length; and every paper/PDF hash matched `corpus/corpus_manifest.json`. No malformed records or duplicate Chunk IDs were found. The path used for this later reconciliation is recorded in Section 10.

Passage alignment normalized Unicode, whitespace and line-break hyphenation, then required the matching paper ID, PDF hash and page. `HIGH` means one matching exported Chunk; it does not mean a human approved its role. Full texts remain in the private export under the IDs below. The final column now reflects Section 10's current review state; the original mapping results and warnings are preserved.

| Candidate | Approved passage | Mapping / full-text reference | Proposed whole-Chunk role | Warning | Whole-Chunk approval |
|---|---|---|---|---|---|
| ML01 | METHOD | `651d3ede…eed0` | METHOD | — | APPROVED — NeelSabharwal, 2026-10-22 |
| ML02 | METHOD | unresolved: `99d443f9…8df9`; `c664046a…b74a` | METHOD (each) | 200-character overlap | UNRESOLVED — no approval |
| ML03 | METHOD | `b351a904…21b4` | METHOD | — | APPROVED — NeelSabharwal, 2026-10-22 |
| ML04 | EVALUATION | `d1c3c5ec…e1d9` | EVALUATION | — | APPROVED — NeelSabharwal, 2026-10-22 |
| ML05 | EVALUATION | `94ceea71…0bc9` | EVALUATION | figure-caption residue | APPROVED — NeelSabharwal, 2026-10-22 |
| ML06 | EVALUATION | `03859e00…87ce` | EVALUATION | table plus results prose | APPROVED — NeelSabharwal, 2026-10-22 |
| ML07 | AMBIGUOUS/EXCLUDE | `697581cc…71eb` | AMBIGUOUS/EXCLUDE | title/abstract/intro mix | EXCLUDED — not a pilot label |
| ML08 | METHOD | `24bfdc54…4b2` | METHOD | — | APPROVED — NeelSabharwal, 2026-10-22 |
| ML09 | METHOD | `62a59ed9…581d` | METHOD | — | APPROVED — NeelSabharwal, 2026-10-22 |
| ML10 | METHOD | unresolved: `62a59ed9…581d`; `c11cac78…b01` | METHOD (each) | 200-character overlap | UNRESOLVED — no approval |
| ML11 | EVALUATION | `d150f9c0…bef` | EVALUATION | — | APPROVED — NeelSabharwal, 2026-10-22 |
| ML12 | EVALUATION | `e03be809…5d9d` | EVALUATION | — | APPROVED — NeelSabharwal, 2026-10-22 |
| ML13 | EVALUATION | `90c47b49…9011` | EVALUATION | — | APPROVED — NeelSabharwal, 2026-10-22 |
| ML14 | AMBIGUOUS/EXCLUDE | `ec356bbd…caa7` | AMBIGUOUS/EXCLUDE | title/abstract mix | EXCLUDED — not a pilot label |
| ML15 | METHOD | `abeb54c8…5d9a` | METHOD | — | APPROVED — NeelSabharwal, 2026-10-22 |
| ML16 | METHOD | `242f1e4e…1c7d` | METHOD | — | APPROVED — NeelSabharwal, 2026-10-22 |
| ML17 | METHOD | unresolved: `06c89eae…3ce0`; `70211c11…58da` | METHOD (each) | 200-character overlap | UNRESOLVED — no approval |
| ML18 | EVALUATION | `fc1c8aea…358a` | EVALUATION | same Chunk as ML21 | APPROVED — NeelSabharwal, 2026-10-22 |
| ML19 | EVALUATION | `a85d62e0…2278` | EVALUATION | — | APPROVED — NeelSabharwal, 2026-10-22 |
| ML20 | EVALUATION | `32429084…a7ad` | EVALUATION | — | APPROVED — NeelSabharwal, 2026-10-22 |
| ML21 | AMBIGUOUS/EXCLUDE | `fc1c8aea…358a` | EVALUATION | duplicate of ML18; passage exclusion is unchanged | EXCLUDED — not a pilot label |

Result: 18 candidates have a single exact normalized-text match; ML02, ML10 and ML17 each match two overlapping Chunks and retain no single `chunk_id`. ML18 and ML21 share one mapped Chunk, so the distinct eligible set is 15 Chunks: 6 METHOD and 9 EVALUATION (DPR 2/3, RAG 2/3, GraphRAG 2/3). ML07 and ML14 remain excluded mixed-content Chunks; ML21 remains an excluded passage/duplicate candidate, not an additional training Chunk. Independent approval in Section 10 now supports `actual_chunk_role_verified=YES` for the 15 eligible rows only. The other six retain `NO`.

## 9. Student acceptance of AI-reviewed recommendations — 2026-10-21

**Student:** Fabrice Afopa. **Acceptance scope:** acceptance of the documented AI-reviewed recommendations, **not** a statement that the student independently inspected every complete Chunk. Passage-level approvals from 2026-10-21 are preserved.

- **Accepted AI recommendations for 15 unique Chunks:** METHOD — ML01, ML03, ML08, ML09, ML15, ML16 (6); EVALUATION — ML04, ML05, ML06, ML11, ML12, ML13, ML18, ML19, ML20 (9).
- **EXCLUDED (3):** ML07 and ML14 are unsuitable title/abstract mixed-content Chunks; ML21 is excluded from training because it duplicates ML18, while its distinct approved passage-level exclusion remains intact.
- **UNRESOLVED, not training data (3):** ML02, ML10 and ML17 each have two overlapping source Chunks. The complete supporting Chunks are method-oriented, but no single actual Chunk ID is selected because the source passage lies in the overlap.

At this historical acceptance step, the CSV used `review_status=APPROVED`, `actual_chunk_role_verified=YES` and `training_eligibility=ELIGIBLE_UNIQUE` for those 15 rows. Those fields alone did **not** establish independent human whole-Chunk review. Fabrice's original `student_reviewer` / `student_reviewed_at`, `ai_recommendation` and all `student_acceptance_*` fields are preserved as history, including the explicit scope limitation. The current independent-review fields and pilot eligibility gate below distinguish the later confirmation without rewriting his contribution.

## 10. Independent complete-Chunk approval — 2026-10-22

**Independent human reviewer:** `NeelSabharwal`. **Review date:** `2026-10-22`.
The team lead explicitly states that he personally reviewed the 15 uniquely mapped,
complete Neo4j Chunks and confirms their proposed METHOD/EVALUATION labels for the
ML pilot. This records that supplied confirmation; it does not claim a new inspection
by the assistant, an additional PDF review, a blinded second-label exercise or
adjudication. No time of day or timezone is invented for the review date.

- **Approved METHOD (6):** ML01, ML03, ML08, ML09, ML15, ML16.
- **Approved EVALUATION (9):** ML04, ML05, ML06, ML11, ML12, ML13, ML18, ML19, ML20.
- **Unresolved (3):** ML02, ML10, ML17; both overlapping references remain recorded,
  no single Chunk is selected, and no independent whole-Chunk label is assigned.
- **Excluded (3):** ML07, ML14, ML21; no reviewed pilot label is assigned. ML21 still
  references the same Chunk as ML18, so only ML18 contributes that approved Chunk.

The CSV distinguishes the layers as follows:

| Fields | Meaning |
|---|---|
| `proposed_label`, `exact_supporting_excerpt`, `passage_review_*`, `passage_reviewer` | Original passage-level proposals and Fabrice's decisions; unchanged. |
| `mapping_status`, `mapping_confidence`, `supporting_chunk_ids`, selected `chunk_id`, stored offsets/hash | Technical mapping evidence; unchanged. A match or confidence level is not semantic approval. |
| `ai_recommendation`, `student_acceptance_*`, `student_reviewer`, `student_reviewed_at`, original notes | Preserved Fabrice acceptance/recommendation history; not the independent reviewer identity. |
| `independent_review_status`, `independent_reviewer`, `independent_review_date`, `independent_review_scope` | Current independent confirmation for exactly the 15 named complete Chunks. Unresolved/excluded rows have no independent reviewer/date. |
| `approved_whole_chunk_label`, `whole_chunk_approval`, `actual_chunk_role_verified` | Approved binary label, `APPROVED`, and `YES` for the 15; no binary approval for the other six. |
| `training_eligibility` | `ELIGIBLE_REVIEWED_PILOT` for those 15 only; `UNRESOLVED_NOT_TRAINING` or `EXCLUDED` for the remainder. |

Use the explicit independent-review fields together with a unique selected mapping
and approved binary label as the eligibility gate; legacy `review_status` or AI
acceptance alone is insufficient. All rows remain `DEVELOPMENT_ONLY`. Independent
confirmation does not make these exposed labels an unseen test set or satisfy the
future blinded-review protocol. No training, evaluation, predictions or class
balancing were performed. Three-paper generalization limitations remain unchanged.

Only the annotation CSV is allowlisted under `data/ml/`; full/private exports stay
ignored there and under `data/processed/`. The existing local operational export at
`data/processed/ml/chunk_export_for_review.json` can support technical checks without
being copied into the PR or used to infer additional human approvals.

### Technical reconciliation checks — 2026-10-22

CSV validation passed for 21 candidate rows and 42 unique columns, with no missing
cells or duplicate candidate IDs. The selected approved set contains 15 unique
Chunk IDs (6 METHOD / 9 EVALUATION); each paper contributes 2 / 3. All 35 unchanged
original CSV columns, including passages, mapping references, offsets/hashes and
Fabrice's review history, were compared against PR head `8cfef5a`. The two updated
original fields are `whole_chunk_approval` and `training_eligibility`; five explicit
independent-review/label columns were added. The original rubric, candidate table
and 21 exact passage excerpts are unchanged.

Read-only checks of the existing private export verified all 153 UTF-8 text hashes,
offset lengths and paper/PDF identities against the corpus manifest. All 21 candidate
mapping sets matched after NFKC normalization, soft-hyphen removal, dehyphenating
hyphen-plus-whitespace (the stored text collapses line breaks to spaces), and
whitespace removal. The 15 selected mappings' stored offsets and hashes are unchanged.
These checks establish technical consistency, not semantic label correctness; the
independent approval above is based on NeelSabharwal's explicit confirmation.

Ignore-rule checks confirmed that only the annotation CSV is trackable under
`data/ml/`, while full exports, other private data, `.env` and downloaded PDFs stay
ignored. Conflict-marker and Git whitespace checks passed. Application tests were
not rerun for this annotation/documentation reconciliation, and no database connection,
training or evaluation was performed.
