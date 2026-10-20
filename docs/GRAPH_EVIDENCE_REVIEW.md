# Graph Evidence and Entity Alias Review — Project 8

**Project:** AI Research GraphRAG Assistant (Level 3+)  
**Date:** 2026-10-20 | **Deadline:** 2026-10-23  
**Review type:** AI-assisted source and data-model review; **all student approvals: PENDING**  
**Scope:** C03, C09 and GE01–GE20 (eight priority candidates plus twelve additional candidates). **No Neo4j review action, merge, GDS run or application test was performed.**

## 1. Methodology and source integrity

Read the supplied `GRAPH_EVIDENCE_CANDIDATES.csv`, `citation_evidence.csv`, `corpus_manifest.json`, `ENTITY_ALIAS_REVIEW.md`, `ARCHITECTURE.md` and `GDS_READINESS.md`, alongside the **uploaded pinned v1 PDFs**:

- **DPR:** Karpukhin et al., *Dense Passage Retrieval for Open-Domain Question Answering*, [arXiv:2004.04906v1](https://arxiv.org/pdf/2004.04906v1) (10 PDF pages).
- **RAG:** Lewis et al., *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*, [arXiv:2005.11401v1](https://arxiv.org/pdf/2005.11401v1) (18 PDF pages).
- **GraphRAG:** Edge et al., *From Local to Global: A Graph RAG Approach to Query-Focused Summarization*, [arXiv:2404.16130v1](https://arxiv.org/pdf/2404.16130v1) (15 PDF pages).

All three uploaded PDF **byte SHA-256 digests and page counts match** the pinned prototype records in `corpus_manifest.json`. Checked the actual full passages surrounding the CSV excerpts, including experimental contexts and relevant result tables; visually inspected the rendered RAG/GraphRAG bibliography pages and principal method/data pages. A phrase appearing on a page is **not by itself** proof that its associated predicate is correct: `EVALUATED_ON` requires an author-described experiment; `USES` requires application by the authors rather than related-work mention.

**Coordinate reproducibility:** The CSV specifies `pypdf 6.10.0` extraction. The independent inspection environment has `pypdf 5.9.0`: all **20/20 exact excerpt strings were locatable on their stated PDF pages**, but only **6/20** candidates reproduced the recorded page hash, context hash and excerpt offset under 5.9.0 (GE15–GE20); **14/20** did not. This is a parser-version reproducibility limitation, **not evidence of an incorrect source page or relationship**. C03 and C09's bibliography page hashes and title offsets did reproduce in 5.9.0. Re-run the original coordinates with 6.10.0 before automated offset-based approval; never silently shift offsets or edit hashes.

**Status meaning:** `APPROVE_RECOMMENDED` is an AI-assisted recommendation for a source-grounded, *qualified* relation, **not** a student-verified database fact. `REJECT_RECOMMENDED` means the proposed assertion should not be accepted as written. `NEEDS_CLARIFICATION` means a material predicate/identity/scope detail must be resolved before approval. `NOT_CHECKED` means source evidence was not inspected. No student identity or review time is claimed or supplied here.

## 2. Bibliography citations — priority

| ID | Source evidence and direction | Assessment | AI recommendation |
| --- | --- | --- | --- |
| **C03** | [RAG v1 PDF p. 13, reference **[22]**](https://arxiv.org/pdf/2005.11401v1#page=13): entry names Karpukhin et al. and *Dense Passage Retrieval for Open-Domain Question Answering*, with work ID `arXiv:2004.04906`. **RAG → DPR.** | Author/title/work identity and direction agree with CSV. The reference does **not** append `v1`; `selected_target_paper_id=arxiv:2004.04906v1` is a prototype representative, not evidence that v1 was the consulted version. Keep `target_work_id` and `target_version_as_cited=unspecified`. | **APPROVE_RECOMMENDED** for **work-level** citation only. |
| **C09** | [GraphRAG v1 PDF p. 13, Lewis et al. (2020)](https://arxiv.org/pdf/2404.16130v1#page=13): full RAG title and Lewis-led author list appear in the bibliography, as a NeurIPS paper. **GraphRAG → RAG.** | Author/title/work identity and direction agree. The entry gives published-work metadata, not `arXiv:2005.11401v1` or a consulted preprint revision. Preserve `target_version_as_cited=unspecified`. | **APPROVE_RECOMMENDED** for **work-level** citation only. |

**Directed path (conditional on human approval):** GraphRAG → RAG → DPR, supported by **two independently sourced `CITES` claims**, C09 and C03. Do not label this an existing Neo4j path or shortest path until the claims are reviewed, imported and queried.

## 3. Priority scientific dataset relations (eight)

Every row's `student_review_status` stays **PENDING**. The evidence location is a **1-based PDF page**.

| ID | Claim and PDF passage | Source-context interpretation; qualification | AI recommendation |
| --- | --- | --- | --- |
| **GE03** | DPR `EVALUATED_ON` Natural Questions — [DPR p. 4, §4.2](https://arxiv.org/pdf/2004.04906v1#page=4) | Listed in the authors' five QA datasets; DPR §5 and Table 2 (p. 6) report retrieval results. Not merely cited background. Preserve this paper's preparation and splits. | **APPROVE_RECOMMENDED** |
| **GE04** | DPR `EVALUATED_ON` TriviaQA — [DPR p. 4, §4.2](https://arxiv.org/pdf/2004.04906v1#page=4) | Experimental dataset, called `Trivia` in the DPR passage. DPR §5/Table 2 confirms evaluation. No claim of a particular TriviaQA Wiki/Web split in this relationship. | **APPROVE_RECOMMENDED** |
| **GE05** | DPR `EVALUATED_ON` WebQuestions — [DPR p. 4, §4.2](https://arxiv.org/pdf/2004.04906v1#page=4) | `WebQuestions (WQ)` is explicitly a dataset in the experimental setup, also in DPR's p. 6 results. No automatic equivalence to WebQuestionsSP. | **APPROVE_RECOMMENDED** |
| **GE06** | DPR `EVALUATED_ON` CuratedTREC — [DPR p. 4, §4.2](https://arxiv.org/pdf/2004.04906v1#page=4) | Dataset is explicitly `CuratedTREC (TREC)` in authors' evaluation; p. 6 reports results. `TREC` alone outside this expansion is ambiguous. | **APPROVE_RECOMMENDED** |
| **GE11** | RAG `EVALUATED_ON` Natural Questions — [RAG p. 4, §3.1](https://arxiv.org/pdf/2005.11401v1#page=4) | Named among four open-domain QA datasets selected by the authors; RAG p. 6 Table 1 reports results. RAG uses a generative answer procedure unlike DPR's extractive reader. | **APPROVE_RECOMMENDED** |
| **GE12** | RAG `EVALUATED_ON` TriviaQA — [RAG p. 4, §3.1](https://arxiv.org/pdf/2005.11401v1#page=4) | `TriviaQA (TQA)` is an experimental dataset; RAG p. 6 Table 1 distinguishes two TQA test splits. Do not merge those evaluation *settings* even if the benchmark name is shared. | **APPROVE_RECOMMENDED** |
| **GE13** | RAG `EVALUATED_ON` WebQuestions — [RAG p. 4, §3.1](https://arxiv.org/pdf/2005.11401v1#page=4) | `WebQuestions (WQ)` appears in the experimental task list and p. 6 results; preprocessing and RAG initialization decisions remain source-specific. | **APPROVE_RECOMMENDED** |
| **GE14** | RAG `EVALUATED_ON` CuratedTREC — [RAG p. 4, §3.1](https://arxiv.org/pdf/2005.11401v1#page=4) | `CuratedTrec (CT)` appears among four evaluated datasets; RAG pp. 4–5 describes special handling of regular-expression answers. Alias at dataset level only. | **APPROVE_RECOMMENDED** |

**Priority conclusion:** Four cross-paper dataset joins are defensible **after independent student approval of both source-specific claims and the aliases**. They say the authors evaluated on the same *named benchmark families*, **not** that their metrics, experimental protocols or results are directly comparable.

## 4. Additional twelve candidates

| ID | Evidence and reviewed interpretation | AI recommendation |
| --- | --- | --- |
| **GE01** | [DPR p. 3, §3.1](https://arxiv.org/pdf/2004.04906v1#page=3): two independent base-uncased BERT encoders are part of the DPR method. `Paper USES Method(BERT-base)` supported; no cross-paper checkpoint identity. | **APPROVE_RECOMMENDED** with architecture-level scope. |
| **GE02** | [DPR p. 2, §2](https://arxiv.org/pdf/2004.04906v1#page=2): authors define/study extractive open-domain textual QA and passage retrieval. `ADDRESSES` appropriate. | **APPROVE_RECOMMENDED** |
| **GE07** | [RAG p. 3, §2.2](https://arxiv.org/pdf/2005.11401v1#page=3): authors explicitly use a DPR-based pretrained retriever. `USES` is separate from the bibliography citation C03. | **APPROVE_RECOMMENDED** |
| **GE08** | [RAG p. 3, §2.2](https://arxiv.org/pdf/2005.11401v1#page=3): DPR-based retriever is described as containing BERT-base encoders, and RAG uses that pretrained bi-encoder. `USES BERT-base` follows through the stated component design; **not** proof of an identical trained DPR checkpoint or casing. | **APPROVE_RECOMMENDED** with explicit inherited-component qualifier. |
| **GE09** | [RAG p. 3, §2.3](https://arxiv.org/pdf/2005.11401v1#page=3): authors directly state that they use BART-large as generator. Do not merge it with generic BART/BERT. | **APPROVE_RECOMMENDED** |
| **GE10** | [RAG p. 4, §3.1](https://arxiv.org/pdf/2005.11401v1#page=4): authors tackle open-domain QA by answer generation, unlike DPR's extractive reader. The broad `ADDRESSES` task join is valid, not method equivalence. | **APPROVE_RECOMMENDED** |
| **GE15** | [GraphRAG p. 4, §2.4](https://arxiv.org/pdf/2404.16130v1#page=4): authors explicitly select **Leiden** for hierarchical community detection. Their method is not Louvain. | **APPROVE_RECOMMENDED** |
| **GE16** | [GraphRAG p. 3, end of §1](https://arxiv.org/pdf/2404.16130v1#page=3) and [p. 5, §2.6](https://arxiv.org/pdf/2404.16130v1#page=5): uses a map-reduce *summarization approach* (parallel partial answers, global synthesis), not necessarily Hadoop/software MapReduce. | **APPROVE_RECOMMENDED** with workflow qualifier. |
| **GE17** | [GraphRAG p. 1, abstract](https://arxiv.org/pdf/2404.16130v1#page=1): aims at query-focused summarization for corpus-wide sensemaking. Keep separate from factoid QA as task identity. | **APPROVE_RECOMMENDED** |
| **GE18** | [GraphRAG p. 6, §3.1](https://arxiv.org/pdf/2404.16130v1#page=6): experimentally uses the **Behind the Tech** podcast transcript collection. Scope the proposed dataset entity to this paper's constructed corpus, not all podcasts. | **APPROVE_RECOMMENDED** with scoped dataset ID. |
| **GE19** | [GraphRAG p. 6, §3.1](https://arxiv.org/pdf/2404.16130v1#page=6): experimentally uses news articles from the MultiHop-RAG corpus for global sensemaking questions; does **not** imply using its original benchmark labels. | **APPROVE_RECOMMENDED** with scoped dataset ID. |
| **GE20** | [GraphRAG p. 3, §2.1/Figure 2](https://arxiv.org/pdf/2404.16130v1#page=3): uses a HotPotQA sample **to examine chunk-size and entity-extraction behavior**, not as its main end-to-end global-answer benchmark. `EVALUATED_ON` is defensible only with `evaluation_stage=entity_extraction` (or equivalent preserved qualifier). | **APPROVE_RECOMMENDED** **conditional on preserving component-only scope**; otherwise **NEEDS_CLARIFICATION**. |

No candidate was rejected solely for sharing vocabulary with another paper. Conversely, quote matching or `SOURCE_LOCATED` never means a student has semantically approved any of these 20 claims.

## 5. Proposed entity-alias decisions (all human approval pending)

| Canonical entity proposal | Evidence IDs / forms | AI recommendation and limit |
| --- | --- | --- |
| **Dataset: Natural Questions** | GE03, GE11; `NQ` | **APPROVE_RECOMMENDED:** same named benchmark, not necessarily same splits/preprocessing. |
| **Dataset: TriviaQA** | GE04 `Trivia`; GE12 `TQA` | **APPROVE_RECOMMENDED:** same named benchmark; keep Web/Wiki split qualifiers distinct. |
| **Dataset: WebQuestions** | GE05, GE13; `WQ` | **APPROVE_RECOMMENDED:** exact expansion; do not conflate with WebQuestionsSP. |
| **Dataset: CuratedTREC** | GE06 `TREC`; GE14 `CuratedTrec/CT` | **APPROVE_RECOMMENDED:** source-supported expansions only. Bare `TREC` elsewhere is ambiguous. |
| **Method: BERT-base** | GE01, GE08 | **APPROVE_RECOMMENDED** at encoder architecture level; **NEEDS_CLARIFICATION** for model checkpoint/casing identity. |
| **Task: Open-domain question answering** | GE02, GE10 | **APPROVE_RECOMMENDED** at task-family level; extractive versus generative procedures stay distinct. |
| **DPR / BART-large / Leiden / map-reduce summarization** | GE07 / GE09 / GE15 / GE16 | **APPROVE_RECOMMENDED** for separately typed Methods with qualifiers; `DPR` Method ≠ DPR Paper. Leiden ≠ Louvain. |
| **QFS, Behind the Tech corpus, MultiHop-RAG news corpus, HotPotQA** | GE17–GE20 | **APPROVE_RECOMMENDED** as distinct scoped Task/Datasets; preserve component-only qualifier for HotPotQA and original-versus-derived corpus distinction. |

**Implementation caution:** Shared `object_proposed_id` values in the CSV express proposed aliases, **not** an authorized database merge. Preserve source surfaces, context, individual claim IDs and any contested variants until the reviewer explicitly approves each mapping. No alias merge has been performed here.

## 6. Corrections, uncertainties and GDS implications

1. **No mandatory scientific-row corrections identified** for GE03–GE06 and GE11–GE14. Keep their `EVALUATED_ON` predicate and source-specific qualifiers. Do not change any pinned PDF hashes, coordinates, object IDs or citation directions automatically.
2. **Require work-level citation semantics:** for C03/C09 retain `target_version_as_cited=unspecified`; a pinned version-specific `Paper` node is a navigation representative, not documentary evidence of the edition cited.
3. **Preserve narrow extraction contexts:** GE08's BERT-base use is inherited via DPR; GE20's HotPotQA use is an extraction-component experiment; GE18/GE19 name scoped experiment corpora. If the target graph cannot retain these qualifiers, defer those rows instead of creating misleading broad assertions.
4. **Offset verification outstanding:** rerun the 20 original excerpt/page/context hash checks using `pypdf==6.10.0` and unchanged PDFs/CSV before any programmatic offset acceptance. The 5.9.0 mismatch must not be silently patched.
5. **Graph traversal:** after student approval, four shared `Dataset` entities would support DPR ↔ dataset ↔ RAG paths backed by two `EVALUATED_ON` claims each. This is not a directed citation path and not proof of identical evaluation performance. C03/C09 separately permit a directed citation chain when approved.
6. **GDS:** the proposed paper similarity graph uses only `SOURCE_VERIFIED` relations and **approved** aliases to form distinct per-paper entity sets and Jaccard-weighted `SHARES_ENTITY` adjacency. In the deliberately bounded 20-candidate *all-approved* fixture, the supporting GDS planning document predicts three papers, one DPR–RAG logical edge, and GraphRAG as an isolate; **this is conditional arithmetic, not a live projection or measured PageRank/Louvain result**. Never include pending claims to make a graph appear connected. A tiny graph cannot justify substantive community or scientific-importance conclusions.

## 7. Student review and acceptance gate

**Current status: AI recommendations recorded; all student approval fields PENDING; no reviewed Neo4j `SOURCE_VERIFIED` promotion, alias merge, traversal or GDS result.** Before final approval:

- [ ] **C03:** visually inspect RAG v1 PDF p. 13, reference [22], and check author, title, work identifier, direction and unspecified target version.
- [ ] **C09:** visually inspect GraphRAG v1 PDF p. 13, Lewis et al. (2020), and check published-work match, direction and unspecified target version.
- [ ] **GE03–GE06:** DPR p. 4 §4.2 **and p. 6 Table 2**; independently confirm four datasets are evaluated, not merely mentioned.
- [ ] **GE11–GE14:** RAG p. 4 §3.1, p. 5 continuation **and p. 6 Table 1**; confirm dataset names and specific split/coding caveats.
- [ ] **Aliases:** separately sign off on NQ, TriviaQA, WQ, CuratedTREC; verify that names refer to a shared benchmark *family* without claiming equivalent evaluation settings.
- [ ] **Remaining candidates:** check GE01–GE02, GE07–GE10 and GE15–GE20 at linked pages, particularly inherited BERT-base use and component-only HotPotQA evaluation.
- [ ] **Reproducibility:** rerun source text hash and offset verification under the specified `pypdf==6.10.0`; investigate rather than silently edit any discrepancy.
- [ ] **Review record:** decide on each candidate and alias with actual reviewer identity, timestamp, source notes, accepted qualifiers and resolved chunk IDs, then obtain teammate review of this Markdown PR. None of these actions is marked complete here.

### Independent passage inspection — 20 October 2026

**Personally inspected:**

- **C03:** RAG bibliography, PDF page 13, reference [22]. Confirmed that RAG cites the DPR work; the cited version is unspecified.
- **C09:** GraphRAG bibliography, PDF page 13. Confirmed that GraphRAG cites Lewis et al.'s RAG work; the cited version is unspecified.
- **GE03–GE06:** DPR, PDF page 6, Table 2. Confirmed evaluation results for the four named datasets. DPR §4.2 should also be checked if not yet inspected.
- **GE11–GE14:** RAG, PDF page 4, §3.1, and page 6, Table 1. Confirmed four named QA datasets and the distinct TriviaQA evaluation splits.

**AI-assisted checks:** Reviewed recommendations for GE01–GE20 and entity aliases. Technical qualifications remain in the review document. These are not recorded as independently approved database claims.

**Outstanding:** Personal checks of remaining passages and aliases, pypdf 6.10.0 coordinate verification, formal claim approval, and Neo4j testing.

No claims were promoted to `SOURCE_VERIFIED`, and no alias merges were performed.

**Overall decision:** **DRAFT FOR INDEPENDENT STUDENT REVIEW**. Both citations and the eight priority dataset candidates are supported at the named-work/named-dataset level, but nothing has been human approved or demonstrated in the live graph.
