# ML labeling review — Method vs Evaluation Chunk classification

**Project:** Project 8 — AI Research GraphRAG Assistant (Level 3+)  
**Deadline:** 2026-10-23  
**Review type:** AI-assisted **passage-candidate proposal**, **not approved Chunk labels**  
**Student annotation status:** **PENDING for every row**  
**Database/ML operations:** **NOT PERFORMED** — no Neo4j writes, training, prediction, evaluation or performance numbers.

## 1. Authority, sources and reproduction

The professor’s [`projects_spec.md`](../docs/requirements/projects_spec.md) (Project 8 and Graph Data Science/Agentic section) and [`project_checklist.md`](../docs/requirements/project_checklist.md) permit a **node-classification ML workflow (3 points)**. This labeling file by itself does not meet that rubric item. The repository’s [`ML_RECOMMENDATION.md`](ML_RECOMMENDATION.md), [`ARCHITECTURE.md`](ARCHITECTURE.md) and [`corpus_manifest.json`](../corpus/corpus_manifest.json) specify the provisional Chunk-labeling and leakage-control design. The recommendation’s 8-paper/96-label target is conditional, not an achieved count.

Only the three manifest-pinned **v1** PDFs were used as scientific evidence. Local uploaded bytes were SHA-256 checked against the manifest, and all 21 short excerpts were found as unique text occurrences on the stated PDF pages. A sample of relevant pages was also inspected in rendered form. **Text was extracted with `pypdf 5.9.0` in this review**, whereas the ingestion/manifest records `pypdf 6.10.0`: therefore **no raw-text offsets or generated Chunk IDs are asserted** here. Reproduce the stored Chunk text and coordinates using the ingestion environment before converting passage proposals into labels.

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

Each CSV row intentionally has **empty** `chunk_id`, `chunk_page_start_char`, `chunk_page_end_char`, `mapped_chunk_text_sha256`, `student_reviewer`, `student_reviewed_at` and adjudication fields. `actual_chunk_role_verified=NO`, `review_status=PENDING`, `proposed_split=DEVELOPMENT_ONLY`. **Never derive an alleged real Chunk ID from these page excerpts.** The trained unit is the **existing** Neo4j `Chunk`, not an invented passage ID.

When access to a frozen graph snapshot is available: locate each excerpt in the exact `Paper` version’s linked `Chunk` texts, record real Chunk ID and **stored** page offsets/hash, verify `PART_OF`, original PDF hash and overlap, and examine the *whole* Chunk. Two source passages may map to one Chunk; count it once or exclude if mixed. Record exclusion reasons and every candidate examined, including those rejected. A student must then supply an actual identity, timestamp and decision; the review document itself must not trigger database Claim approval.

## 4. Feasibility and realistic target

**Immediate deliverable:** manually inspect these 21 passages and attempt to map the **18 potentially binary-eligible proposals** to distinct stored Chunks, with three deliberate exclusions as annotation controls. This is a small *review queue*, not a claim that 18 usable labels exist. Stop after mapping if mixed boundaries, poor extraction or repeated overlap reduce the count; report the actual unique eligible numbers by paper and class, without backfilling a quota.

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
- All 21 excerpts were located in PDFs, but their **entire** mapped Chunk has not been checked for dominant role or duplication. No dataset labels have been human-signed.
- The visible prototype previously had very few `MENTIONS` edges; no live graph-feature audit was run for this task. Graph feature sparsity could make the proposed learner infeasible.
- Dataset preparation text and training recipes can mix Method/Evaluation; final decisions require full context and explicit exclusion when no dominant role exists.
- Do not assign GraphRAG to a scored test set using these publicly exposed suggestions without a controlled, frozen annotation/evaluation protocol; all candidates are currently development review material.
- No Python application code, Neo4j records, evaluation gold annotations, source manifests, or teammate branches were changed.

## 7. What I must personally inspect before approving (exact passages)

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

**Approval declaration (to be filled by the student, not AI):** reviewer `________`; date/time `________`; verified real Chunk IDs `________`; exclusions/decisions `________`. Until filled and independently checked, **all labels remain PENDING**.
