# Graph Evidence and Entity Alias Review — Project 8

**Project:** AI Research GraphRAG Assistant (Level 3+)
**Updated:** 2026-10-21 (Europe/Paris) | **Deadline:** 2026-10-23
**Review type:** AI-assisted source and data-model review; **22/22 qualified scientific claims APPROVED; 21/21 alias recommendations have recorded student decisions (A17 remains NEEDS_CLARIFICATION)**
**Scope:** C03, C09 and GE01–GE20 (eight priority candidates plus twelve additional candidates). **No Neo4j review action, merge, GDS run or application test was performed.**

## 1. Methodology and source integrity

**Verification provenance:** the source-inspection and pypdf execution reports in sections 1, 7 and 8 are retained from the supplied earlier Work review, not independently rerun during final submission verification. This final pass checks documentation and Git state only. Student source inspection is attested by fabrice12345C in the submission request; its earlier date/time was not supplied. No source-inspection timestamp is inferred from today's sign-off recording date.

Read the supplied `GRAPH_EVIDENCE_CANDIDATES.csv`, `citation_evidence.csv`, `corpus_manifest.json`, `ENTITY_ALIAS_REVIEW.md`, `ARCHITECTURE.md` and `GDS_READINESS.md`, alongside the **exact pinned v1 PDFs freshly downloaded from arXiv in the earlier Work session**:

- **DPR:** Karpukhin et al., *Dense Passage Retrieval for Open-Domain Question Answering*, [arXiv:2004.04906v1](https://arxiv.org/pdf/2004.04906v1) (10 PDF pages).
- **RAG:** Lewis et al., *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*, [arXiv:2005.11401v1](https://arxiv.org/pdf/2005.11401v1) (18 PDF pages).
- **GraphRAG:** Edge et al., *From Local to Global: A Graph RAG Approach to Query-Focused Summarization*, [arXiv:2404.16130v1](https://arxiv.org/pdf/2404.16130v1) (15 PDF pages).

All three downloaded PDF byte SHA-256 digests, version markers and page counts independently match `corpus_manifest.json`. Page numbers below are **1-based PDF pages**, not zero-based parser indexes. Full page text, the cited passages and surrounding methods/experimental context were read. Additional rendered-page inspections are listed in §8. A method or dataset mentioned only in related work is insufficient for USES or EVALUATED_ON.

**Repository provenance:** baseline review is the existing PR #5 document at head `feb3c9dc481799acb1346de75a70d581b390419b` (blob `571c9bf391c4a4788c369741d6fe6e0070bb8211`). Manifest, citation CSV, architecture, course requirements, `AGENTS.md`, evaluation review and evaluation verifier were read from that head. Main was also checked. The candidate CSV, alias review and GDS readiness files are absent from both that PR head and main; their actual paths were found on `feat/agent-evidence`, pinned to `bca43cae42f821600f9e07ec91a6df71e3349f28`. That commit also supplies `scripts/verify_research_handoff.py`, `docs/RESEARCH_INTEGRATION.md` and `data/evaluation/evaluation_gold.json`. These are supporting inputs, not files added to PR #5 by this task. Do not merge the implementation branch simply to publish this review. The two attached course files and repository requirement copies were both read; no grading requirement is marked fulfilled by this document.

**Coordinate reproducibility update:** the baseline reported 6/20 scientific candidates reproducing under pypdf 5.9.0 (and 20/20 excerpts located). That is a historical reported result, not a rerun in the earlier Work session. The earlier Work session independently installed **pypdf 6.10.0** and checked unchanged inputs: **20/20 scientific candidates**, **20/20 separate gold evidence records**, and **C03/C09 bibliography page hashes/title offsets all pass**. §7 separates these source-only checks from the repository's previously reported live-database audit. No PDF, excerpt, hash, offset, CSV or gold record was corrected to obtain a pass.

**Status meaning:** `APPROVE_RECOMMENDED` is an AI-assisted recommendation for a source-grounded, *qualified* relation, **not** a student-verified database fact. `REJECT_RECOMMENDED` means the proposed assertion should not be accepted as written. `NEEDS_CLARIFICATION` means a material predicate/identity/scope detail must be resolved before approval. `NOT_CHECKED` means source evidence was not inspected. Student decisions and their provenance are recorded separately in section 9; recommendations alone do not constitute student approval.

## 2. Bibliography citations — priority

| ID | Source evidence and direction | Assessment | AI recommendation |
| --- | --- | --- | --- |
| **C03** | [RAG v1 PDF p. 13, reference **[22]**](https://arxiv.org/pdf/2005.11401v1#page=13): entry names Karpukhin et al. and *Dense Passage Retrieval for Open-Domain Question Answering*, with work ID `arXiv:2004.04906`. **RAG → DPR.** | Author/title/work identity and direction agree with CSV. The reference does **not** append `v1`; `selected_target_paper_id=arxiv:2004.04906v1` is a prototype representative, not evidence that v1 was the consulted version. Keep `target_work_id` and `target_version_as_cited=unspecified`. | **APPROVE_RECOMMENDED** for **work-level** citation only. |
| **C09** | [GraphRAG v1 PDF p. 13, Lewis et al. (2020)](https://arxiv.org/pdf/2404.16130v1#page=13): full RAG title and Lewis-led author list appear in the bibliography, as a NeurIPS paper. **GraphRAG → RAG.** | Author/title/work identity and direction agree. The entry gives published-work metadata, not `arXiv:2005.11401v1` or a consulted preprint revision. Preserve `target_version_as_cited=unspecified`. | **APPROVE_RECOMMENDED** for **work-level** citation only. |

**Directed work-citation chain (student-approved claims; not materialized):** GraphRAG → RAG → DPR, supported by **two independently sourced `CITES` claims**, C09 and C03. Do not label this an existing Neo4j path or shortest path until the claims are reviewed, imported and queried.

## 3. Priority scientific dataset relations (eight)

All eight qualified claims have student **APPROVED** sign-off in section 9; no database review status was changed. The evidence location is a **1-based PDF page**.

| ID | Claim and PDF passage | Source-context interpretation; qualification | AI recommendation |
| --- | --- | --- | --- |
| **GE03** | DPR `EVALUATED_ON` Natural Questions — [DPR p. 4, §4.2](https://arxiv.org/pdf/2004.04906v1#page=4) | Listed in the authors' five QA datasets; DPR §5 and Table 2 (p. 6) report retrieval results. Not merely cited background. Preserve this paper's preparation and splits. | **APPROVE_RECOMMENDED** |
| **GE04** | DPR `EVALUATED_ON` TriviaQA — [DPR p. 4, §4.2](https://arxiv.org/pdf/2004.04906v1#page=4) | Experimental dataset, called `Trivia` in the DPR passage. DPR §5/Table 2 confirms evaluation. DPR p. 4 footnote 6 explicitly uses unfiltered TriviaQA and discards the Bing evidence documents. Preserve that preparation; RAG Appendix B (p. 17) identifies its DPR-style test split as public Web Development. | **APPROVE_RECOMMENDED** |
| **GE05** | DPR `EVALUATED_ON` WebQuestions — [DPR p. 4, §4.2](https://arxiv.org/pdf/2004.04906v1#page=4) | `WebQuestions (WQ)` is explicitly a dataset in the experimental setup, also in DPR's p. 6 results. No automatic equivalence to WebQuestionsSP. | **APPROVE_RECOMMENDED** |
| **GE06** | DPR `EVALUATED_ON` CuratedTREC — [DPR p. 4, §4.2](https://arxiv.org/pdf/2004.04906v1#page=4) | Dataset is explicitly `CuratedTREC (TREC)` in authors' evaluation; p. 6 reports results. `TREC` alone outside this expansion is ambiguous. | **APPROVE_RECOMMENDED** |
| **GE11** | RAG `EVALUATED_ON` Natural Questions — [RAG p. 4, §3.1](https://arxiv.org/pdf/2005.11401v1#page=4) | Named among four open-domain QA datasets selected by the authors; RAG p. 6 Table 1 reports results. RAG uses a generative answer procedure unlike DPR's extractive reader. | **APPROVE_RECOMMENDED** |
| **GE12** | RAG `EVALUATED_ON` TriviaQA — [RAG p. 4, §3.1](https://arxiv.org/pdf/2005.11401v1#page=4) | `TriviaQA (TQA)` is an experimental dataset; RAG p. 6 Table 1 and p. 17 Appendix B distinguish public TriviaQA Web Development (DPR-style) and official hidden Wiki test. Do not merge these evaluation settings even if the benchmark name is shared. | **APPROVE_RECOMMENDED** |
| **GE13** | RAG `EVALUATED_ON` WebQuestions — [RAG p. 4, §3.1](https://arxiv.org/pdf/2005.11401v1#page=4) | `WebQuestions (WQ)` appears in the experimental task list and p. 6 results; p. 5 describes initialization from the NQ RAG model; p. 17 Appendix B describes separate training pairs for multiple answer annotations. Preserve these source-specific settings. | **APPROVE_RECOMMENDED** |
| **GE14** | RAG `EVALUATED_ON` CuratedTREC — [RAG p. 4, §3.1](https://arxiv.org/pdf/2005.11401v1#page=4) | `CuratedTrec (CT)` appears among four evaluated datasets; RAG pp. 4–5 describes special handling of regular-expression answers. Alias at dataset level only. | **APPROVE_RECOMMENDED** |

**Priority conclusion:** RAG p. 5 explicitly follows prior splitting methods and p. 17 Appendix B explicitly reports using DPR splits, including identification of its TriviaQA open-domain test split. This positive evidence of a shared split convention should be retained, while shared names alone do not establish it. Four cross-paper dataset joins are defensible **after independent student approval of both source-specific claims and the aliases**. They say the authors evaluated on the same *named benchmark families*, **not** that their metrics, experimental protocols or results are directly comparable.

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

## 5. Additional context, limits and corrections

The following checks supplement the retained candidate tables. Each verdict is **APPROVE_RECOMMENDED only for the qualified assertion**. No source contradiction was identified for that narrow assertion; the limiting evidence below rules out broader interpretations.

| IDs | Exact passage to inspect and limiting context | Required interpretation |
| --- | --- | --- |
| GE01 | DPR p. 3 §3.1, **Encoders** paragraph; §3.2 training follows | Two distinct base-uncased BERT networks are actually used. The text acknowledges other possible encoders but selects these. Learned parameters are not an architecture alias. |
| GE02 | DPR p. 2 §2 **Background**, opening definition and extractive-setting paragraph; p. 3 §3 introduction | The paper studies factoid open-domain textual QA and focuses on its retrieval component. ADDRESSES does not mean it solves every QA or summarization task. |
| GE07 | RAG p. 3 §2.2, first paragraph and pretrained-memory paragraph; p. 4 §2.4 continuation | The retriever is initialized from a pretrained DPR bi-encoder; its training data include NQ/TriviaQA. RAG fixes the document encoder/index and fine-tunes the query encoder and generator. This is actual method use, not C03 alone. |
| GE08 | RAG p. 3 §2.2, document/query representation definitions and pretrained-bi-encoder paragraph; p. 4 §2.4 | Both representations use BERT-base architecture **within the DPR component**. The two encoders have different parameter sets; RAG subsequently fine-tunes its query encoder while keeping the document encoder fixed. This does not establish cross-paper checkpoint equality. The passage does not independently establish casing or exact checkpoint identity. |
| GE09 | RAG p. 3 §2.3, generator selection paragraph; p. 4 §2.4 | BART-large is explicitly selected, although other encoder-decoders are possible in principle. It is fine-tuned; no particular downloadable checkpoint hash is established. |
| GE10 | RAG pp. 4–5 §3.1; p. 6 Table 1 and §4.1; p. 7 continuation | Questions/answers are treated as input-output pairs for generation. Comparisons with extractive and closed-book systems do not identify those systems as RAG components. Broad QA task-family overlap with DPR is valid. |
| GE15 | GraphRAG p. 4 §2.4, algorithm-selection paragraph; p. 5 Figure 3 caption | The authors select Leiden for hierarchical communities. Other community algorithms are possible, but **USES Louvain would be unsupported for this implementation**. Our project's planned Louvain analytics are a separate design. |
| GE16 | GraphRAG p. 3 introduction continuation, map-reduce paragraph; p. 5 §2.6, three workflow bullets; p. 7 §3.3 TS condition | Parallel intermediate answers are reduced into a global answer. Preserve Method identity as **map-reduce summarization workflow**. The TS baseline applies the same workflow to source texts; the term alone supplies no Hadoop/framework identity. |
| GE17 | GraphRAG p. 1 abstract; p. 6 §3.2 | Corpus-wide global sensemaking is framed as query-focused summarization (QFS). This does not equate QFS with factoid retrieval or with all open-domain QA. |
| GE18 | GraphRAG p. 6 §3.1 first dataset bullet and §3.2; p. 7 §§3.3–3.4 | Behind the Tech transcripts are compiled for this experiment: 1,669 600-token chunks, 100-token overlap, roughly 1M tokens, as reported by the paper. Questions are generated global questions, evaluated in the paper's comparative setting. These are source-reported experimental sizes, not our graph counts or verified corpus bytes. No universal “Podcast dataset” identity. |
| GE19 | GraphRAG p. 6 §3.1 second dataset bullet and §3.2; p. 7 §§3.3–3.4 | MultiHop-RAG news articles spanning September 2013–December 2023: 3,197 600-token chunks, 100-token overlap, roughly 1.7M tokens, as reported by the paper. Global questions are newly generated (125 per corpus), not assumed to be the original benchmark QA labels. Exact original/derived corpus byte equivalence was not checked. |
| GE20 | GraphRAG p. 3 §2.1 and **Figure 2 caption**; p. 4 §2.2 continuation; contrast p. 6 §§3.1–3.2 | A HotPotQA sample supports a chunk-size/gleanings investigation using the generic extraction prompt with gpt-4-turbo. The measured quantity is **entity references detected**, not an independently established extraction precision/recall score or end-to-end QA accuracy. Main global-answer experiments use the two corpora in §3.1. The dataset mention in §3.2 alone would not establish use. |

**GE20 acceptance condition:** retain `evaluation_stage=entity_extraction`, `COMPONENT_ONLY`, and sample/chunk-size/gleanings context in the claim and downstream explanations. The source CSV already records this condition. If the implementation or student interpretation drops it, the decision must become **NEEDS_CLARIFICATION**, rather than approving an unqualified main-benchmark claim.

**Eight dataset relations rechecked:** DPR p. 4 §4.2, its footnote 6 and continuation at p. 5 Table 1 establish author-selected datasets and preparation; p. 5 §5/§5.1 and p. 6 Table 2 establish actual DPR retrieval experiments, including separate Single/Multi training settings. RAG pp. 4–5 §3.1, p. 6 Table 1/§4.1 and p. 17 Appendix B establish author-selected datasets and actual RAG results. RAG reports exact-match answer scores, while DPR Table 2 reports top-k retrieval accuracy. Repeated names permit benchmark-family joins, not an automatic comparison of the numerical results. The baseline's suggestion that no TriviaQA variant could be specified has been strengthened with the explicit source qualifications above.

**Citation findings retained:** C03 explicitly names Vladimir Karpukhin, Barlas Oguz, Sewon Min, Ledell Wu, Sergey Edunov, Danqi Chen and Wen-tau Yih and the DPR title/arXiv work ID. C09 names Patrick Lewis and coauthors and the RAG title in NeurIPS volume 33, pp. 9459–9474. Author/title identity matches the downloaded target title pages. C03 is **RAG → DPR**; C09 is **GraphRAG → RAG**. Neither bibliography specifies a target arXiv revision; keep `target_version_as_cited=unspecified`. These are work-level citation findings, not claims about which v1 PDF the authors consulted and not evidence of existing Neo4j edges.


## 6. Alias recommendations and mapping boundaries

ACCEPT/REJECT/NEEDS_CLARIFICATION in this table are **AI mapping recommendations**, not student decisions. The first fourteen rows correspond to the fourteen proposed entities in the candidate CSV. Additional rows explicitly reject or defer tempting over-merges. Existing student decisions are recorded in section 9; rejection and deferral recommendations remain binding.

| Group | Proposed mapping | AI alias recommendation | Evidence and boundary |
| --- | --- | --- | --- |
| A01 | Natural Questions ↔ NQ (Dataset) | ACCEPT | DPR p. 4 §4.2; RAG p. 4 §3.1. Same benchmark family; retain splits, answer annotations and preprocessing. |
| A02 | TriviaQA ↔ Trivia (DPR) ↔ TQA (RAG) (Dataset) | ACCEPT | DPR p. 4 §4.2/footnote 6; RAG pp. 4–6 §3.1/Table 1 and p. 17 Appendix B. Restrict shorthand to these contexts; keep Web Development and Wiki test settings distinct. |
| A03 | WebQuestions ↔ WQ (Dataset) | ACCEPT | Explicit expansions in DPR p. 4 §4.2 and RAG p. 4 §3.1. WebQuestionsSP is a distinct variant, not an accepted mapping here. |
| A04 | CuratedTREC ↔ CuratedTrec ↔ CT (RAG) ↔ TREC (DPR) | ACCEPT | DPR p. 4 §4.2; RAG pp. 4–5 §3.1. Only these explicit expansions; generic TREC tracks/corpora are broader. Preserve regex-answer handling. |
| A05 | base-uncased BERT (DPR) ↔ BERT BASE (RAG), architecture-level BERT-base | ACCEPT | DPR p. 3 §3.1; RAG p. 3 §2.2. Keep uncased qualifier on DPR and unspecified casing on this RAG passage; no checkpoint/weight identity. |
| A06 | open-domain textual QA (DPR) ↔ open-domain QA (RAG), Task family | ACCEPT | DPR p. 2 §2; RAG pp. 4–5 §3.1. Keep extractive and generative settings as distinct qualifications. |
| A07 | DPR acronym ↔ Dense Passage Retrieval Method | ACCEPT | RAG p. 3 §2.2 and DPR p. 3 §3. Distinct typed Entity from the DPR Paper/version. |
| A08 | BART-large ↔ BART-large Method spelling | ACCEPT | RAG p. 3 §2.3. Preserve named size/variant; this is an identity entry, not an inference that every BART is BART-large. |
| A09 | Leiden ↔ Leiden Method | ACCEPT | GraphRAG p. 4 §2.4 and p. 5 Figure 3. No Louvain alias. |
| A10 | map-reduce approach ↔ map-reduce summarization workflow | ACCEPT | GraphRAG p. 3 introduction continuation and p. 5 §2.6. Scope to summarization; no software-framework identity. |
| A11 | query-focused summarization ↔ QFS Task | ACCEPT | GraphRAG p. 1 abstract. Global sensemaking is its use context, not an exact alias for all QFS or QA. |
| A12 | podcast transcripts ↔ Behind the Tech transcripts (GraphRAG v1 corpus) | ACCEPT | GraphRAG p. 6 §3.1 first bullet. Use `dataset:graphrag-v1-behind-the-tech-transcripts`; generic podcasts outside this scope are not aliases. Corpus bytes/access unverified. |
| A13 | news articles ↔ MultiHop-RAG news corpus, in GraphRAG's experiment | ACCEPT | GraphRAG p. 6 §3.1 second bullet/§3.2. Use `dataset:multihop-rag-news-corpus`; distinguish source corpus from original QA labels, temporal scope and derived processing. |
| A14 | HotPotQA ↔ HotpotQA (Dataset family, capitalization) | ACCEPT | GraphRAG p. 3 §2.1/Figure 2. Use `dataset:hotpotqa`; preserve sample identity limits and component-only role. |
| A15 | DPR Method = DPR Paper/version | REJECT | RAG §2.2 describes a method; ref. [22] cites a work. Relation between them does not establish node identity. |
| A16 | Leiden = Louvain | REJECT | GraphRAG p. 4 §2.4 names Leiden. Distinct methods; project algorithm choice is separate. |
| A17 | BERT-base entries = identical checkpoint/casing/weights | NEEDS_CLARIFICATION | RAG p. 3 §2.2 plus p. 4 §2.4 do not establish this identity. Do not perform such a merge. |
| A18 | BART-large = BERT or every BART variant | REJECT | RAG p. 3 §§2.2–2.3 distinguishes retriever architecture and generator variant. |
| A19 | map-reduce summarization = Hadoop/particular MapReduce framework | REJECT | GraphRAG p. 5 §2.6 supports a workflow, not framework identity. |
| A20 | QFS = factoid QA | REJECT | GraphRAG p. 1 abstract/p. 6 §3.2 contrasts global sensemaking with explicit fact retrieval. |
| A21 | GraphRAG's MultiHop-RAG experiment = original benchmark QA task/labels | REJECT | GraphRAG p. 6 §3.2 generates new global questions. Shared source articles do not equate experimental tasks. |

Preserve source surface forms, kinds, proposed IDs, per-paper qualifiers and individual claim IDs. Generic TREC/Trivia/Podcast/News strings remain ambiguous outside their explicitly scoped contexts. No database merge or resolved live entity ID is supplied by this review.

## 7. Reproducibility: independent results and limits

All checks below were executed in the earlier Work session with **Python and pypdf 6.10.0**. Downloaded PDFs remain outside Git. Source files were materialized as exact UTF-8 GitHub contents; their Git blob hashes were checked against the retrieved blobs before verification. Source inputs, excerpts and coordinates were not edited.

| Check | Independently performed result |
| --- | --- |
| DPR pinned PDF | SHA-256 `2b03fbde33c88fcf82091e6325806bd2656ca777032471e182c602c76ccdab01`; 10 pages; v1 marker matches |
| RAG pinned PDF | SHA-256 `25b55fd0f7c6c91cbe2c88690a33923077103e8f563d154faa1ce11d3527e601`; 18 pages; v1 marker matches |
| GraphRAG pinned PDF | SHA-256 `33524b3b56910c513affdad8dbf67d14e68edf0572e4debdb09a9f1916463b06`; 15 pages; v1 marker matches |
| Scientific CSV GE01–GE20 | **20/20 PASS**: pinned PDF hash/URL, raw page text SHA-256, valid nested context/excerpt bounds, exact excerpt at recorded offsets, context SHA-256 and parser version |
| Existing evaluation verifier, unchanged | **Exit 0; 20/20 PASS; zero other errors**, for the separate D/R/G evidence registry |
| Citation CSV C03/C09 | **2/2 PASS**: PDF hash, bibliography page text SHA-256, recorded title interval normalized to target work title; both retain unspecified target version |
| Recomputed candidate identity sets | DPR 6, RAG 8, GraphRAG 6 distinct proposed entities; DPR/RAG intersection 6 and union 8; GraphRAG shares none within this fixture |
| Live Neo4j chunk mapping/fingerprint, claim state or CITES edges | **NOT RUN in the earlier Work session** |
| PageRank, Louvain, application/API tests, retrieval evaluation | **NOT RUN in the earlier Work session** |

The unchanged repository command (run in the project checkout after the support files are available) is:

```bash
python -m pip install pypdf==6.10.0
python scripts/verify_evaluation_evidence.py --gold data/evaluation/evaluation_gold.json --pdf-dir data/raw
```

The earlier Work session used the equivalent absolute/local paths to those same files. It did **not** claim that the evaluation verifier checks GE rows: it checks the separate gold registry. A separate source-only check of the CSV performed the following exact algorithm, which can be reproduced without Neo4j:

```python
import csv, hashlib, json
from pathlib import Path
import pypdf

assert pypdf.__version__ == "6.10.0"
root = Path(".")
hash_of = lambda v: hashlib.sha256(v.encode("utf-8") if isinstance(v, str) else v).hexdigest()
manifest = json.loads((root / "corpus/corpus_manifest.json").read_text(encoding="utf-8"))
sources = {p["paper_id"]: p for p in manifest["papers"] if p["selection_stage"] == "prototype"}
pages = {}
for ident, source in sources.items():
    pdf = root / source["suggested_download_path"]
    assert hash_of(pdf.read_bytes()) == source["pdf_access"]["sha256"]
    reader = pypdf.PdfReader(pdf)
    assert len(reader.pages) == source["pdf_access"]["page_count"]
    pages[ident] = [p.extract_text() or "" for p in reader.pages]
    assert ident.removeprefix("arxiv:") in pages[ident][0]
with (root / "corpus/GRAPH_EVIDENCE_CANDIDATES.csv").open(encoding="utf-8", newline="") as handle:
    rows = list(csv.DictReader(handle))
assert {r["candidate_id"] for r in rows} == {f"GE{i:02}" for i in range(1, 21)} and len(rows) == 20
for r in rows:
    source = sources[r["source_paper_id"]]
    number = int(r["pdf_page_1based"])
    assert 1 <= number <= len(pages[r["source_paper_id"]])
    text = pages[r["source_paper_id"]][number - 1]
    a, b, c, d = [int(r[k]) for k in ("excerpt_start_char_0based", "excerpt_end_char_exclusive",
                                    "context_start_char_0based", "context_end_char_exclusive")]
    assert r["pdf_sha256"] == source["pdf_access"]["sha256"]
    assert r["pdf_url"] == source["pdf_url"] + "#page=" + str(number)
    assert r["parser"] == "pypdf" and r["parser_version"] == pypdf.__version__
    assert hash_of(text) == r["page_text_sha256"]
    assert 0 <= c <= a < b <= d <= len(text)
    assert text[a:b] == r["supporting_excerpt"]
    assert hash_of(text[c:d]) == r["context_text_sha256"]
print("Scientific candidates: 20/20 PASS")
normalize = lambda text: "".join(c.lower() for c in text if c.isalnum())
with (root / "corpus/citation_evidence.csv").open(encoding="utf-8", newline="") as handle:
    citations = [r for r in csv.DictReader(handle) if r["evidence_id"] in {"C03", "C09"}]
assert len(citations) == 2
for r in citations:
    source = sources[r["source_paper_id"]]
    text = pages[r["source_paper_id"]][int(r["pdf_page_1based"]) - 1]
    target = next(p for p in sources.values() if p["work_id"] == r["target_work_id"])
    a, b = int(r["title_start_char_0based"]), int(r["title_end_char_exclusive"])
    assert r["source_pdf_sha256"] == source["pdf_access"]["sha256"]
    assert hash_of(text) == r["page_text_sha256"]
    assert normalize(text[a:b]) == normalize(target["title"])
    assert r["target_version_as_cited"] == "unspecified"
print("C03/C09 coordinates: 2/2 PASS; coordinates alone do not establish semantic approval")
```

`verify_research_handoff.py` was read, including its version check, structural checks, raw-coordinate verification, normalized-span mapping, live chunk checks and graph-fingerprint comparison. Unlike the source-only checks above, its `audit()` requires configured Neo4j, live chunks and application modules. It was **not executed** here. `docs/RESEARCH_INTEGRATION.md` at the supporting commit **reports** an earlier successful audit: 20 candidate and 20 gold records mapped to 153 live chunks, zero errors and an unchanged fingerprint. Those are previously reported results, not independent database findings from the earlier Work session. Any live state may have changed since that audit.

The old pypdf 5.9.0 mismatch is resolved for these unchanged source coordinates using 6.10.0. This does not establish full-document extraction quality, semantic student approval, valid current chunk mappings or a working answer system. Bibliography title matching still needs the author/title/direction review in §2. Do not manufacture context offsets for the citation CSV, which records title offsets rather than candidate-style context intervals.

### Input fingerprints

- `corpus/GRAPH_EVIDENCE_CANDIDATES.csv` SHA-256: `6154df1342a92133a18425d4ed5152f38f37b5754ae14c4f9534deffc7d81b10`.
- `corpus/citation_evidence.csv` SHA-256: `296396fe74c1d452ab283fd79f486791ad2e1a4ff9d7f69f6fe12332a7959cb2`.
- `data/evaluation/evaluation_gold.json` SHA-256: `2bbcd0ec3fd62f8cd9513198e52e43c5274e12a202728a891446577508879862`.

These identify the exact checked inputs; they are not replacement values to write into evidence rows.

## 8. Work source inspection ledger

This ledger records assistant actions on 21 October 2026, **not student inspections**. PDF opening/extraction covered all pages for coordinate processing. Semantic reading was concentrated on the following full pages/contexts; only the listed rendered pages were visually inspected.

| Paper | Full page text opened and semantically read | Rendered PDF pages visually inspected |
| --- | --- | --- |
| DPR v1 | p. 1 title/abstract via PDF source; pp. 2–6 full text (task, encoders, datasets/preparation, experimental setup and results) | pp. 4 and 6 |
| RAG v1 | p. 1 title/abstract via PDF source; pp. 3–6 and 13 full text; p. 7 §4.1 continuation; p. 17 Appendix B | pp. 3, 6 and 13 |
| GraphRAG v1 | pp. 1, 3–7 and 13 full text (abstract, pipeline, Figure 2, algorithms, workflow, datasets/queries/metrics and bibliography) | pp. 3, 4, 6 and 13 |

The per-claim ledger below identifies the pages actually checked for each assertion. No unread paper version was substituted. All requested source files were ultimately retrieved; no PDF access failure remains. A direct unauthenticated Git clone failed, so authenticated GitHub connector reads were used. That earlier Work folder was a source snapshot. Final submission verification uses the actual local Git checkout on `docs/graph-evidence-review`.

## 9. Student sign-off: qualified claims approved; alias deferral preserved

**Historical report preserved from baseline, 20 October:** its “Independent passage inspection” section reports personal inspection of C03/C09 on their bibliography pages; GE03–GE06 in DPR p. 6 Table 2; and GE11–GE14 in RAG p. 4 §3.1/p. 6 Table 1. It expressly left DPR §4.2, the remaining twelve and aliases outstanding. This is a record of the baseline's report, not a new student attestation or formal approval. No reviewer identity/date/notes are inferred from it.

**Scientific sign-off:** fabrice12345C explicitly confirms personal inspection and approval of C03, C09 and GE01-GE20, including all documented qualifications. The date below is the **sign-off recording date**, 2026-10-21 (Europe/Paris), not the earlier source-inspection date/time, which was not supplied. The misplaced header value `10/21/2026 at 2:13` has unspecified timezone/AM-PM and is not used as an inspection timestamp. Its HotPotQA scope note is preserved in GE20.

**Alias provenance:** all 21 alias rows already contained APPROVED in the user-edited document before this final pass. Those decisions are preserved as approval of each stated recommendation; no new personal alias approval or earlier review time is inferred. Reviewer attribution follows the submitting student's specified account. Alias dates below record documentation on 2026-10-21, not an inferred earlier inspection time.

| Claim | AI recommendation | Source verification reported by earlier Work review | Student decision | Student reviewer | Sign-off recorded (Europe/Paris) | Accepted scope / qualifications |
| --- | --- | --- | --- | --- | --- | --- |
| C03 | APPROVE_RECOMMENDED (work-level) | RAG p. 13 ref. [22]; target title/author identity | APPROVED | fabrice12345C | 2026-10-21 | Work-level RAG to DPR citation only; cited arXiv revision unspecified. |
| C09 | APPROVE_RECOMMENDED (work-level) | GraphRAG p. 13 Lewis et al.; target title/author identity | APPROVED | fabrice12345C | 2026-10-21 | Work-level GraphRAG to RAG citation only; cited arXiv revision unspecified. |
| GE01 | APPROVE_RECOMMENDED | DPR p. 3 §3.1; §3.2 training | APPROVED | fabrice12345C | 2026-10-21 | Qualified assertion in sections 2-5 approved; retain all per-claim evidence limitations. |
| GE02 | APPROVE_RECOMMENDED | DPR p. 2 §2; p. 3 §3 | APPROVED | fabrice12345C | 2026-10-21 | Qualified assertion in sections 2-5 approved; retain all per-claim evidence limitations. |
| GE03 | APPROVE_RECOMMENDED | DPR p. 4 §4.2/footnote 6; p. 5 setup/Table 1; p. 6 Table 2 | APPROVED | fabrice12345C | 2026-10-21 | Qualified assertion in sections 2-5 approved; retain all per-claim evidence limitations. |
| GE04 | APPROVE_RECOMMENDED | DPR p. 4 §4.2/footnote 6; p. 5 setup/Table 1; p. 6 Table 2 | APPROVED | fabrice12345C | 2026-10-21 | Qualified assertion in sections 2-5 approved; retain all per-claim evidence limitations. |
| GE05 | APPROVE_RECOMMENDED | DPR p. 4 §4.2/footnote 6; p. 5 setup/Table 1; p. 6 Table 2 | APPROVED | fabrice12345C | 2026-10-21 | Qualified assertion in sections 2-5 approved; retain all per-claim evidence limitations. |
| GE06 | APPROVE_RECOMMENDED | DPR p. 4 §4.2/footnote 6; p. 5 setup/Table 1; p. 6 Table 2 | APPROVED | fabrice12345C | 2026-10-21 | Qualified assertion in sections 2-5 approved; retain all per-claim evidence limitations. |
| GE07 | APPROVE_RECOMMENDED | RAG p. 3 §2.2; p. 4 §2.4 | APPROVED | fabrice12345C | 2026-10-21 | Qualified assertion in sections 2-5 approved; retain all per-claim evidence limitations. |
| GE08 | APPROVE_RECOMMENDED | RAG p. 3 §2.2; p. 4 §2.4; DPR p. 3 §3.1 | APPROVED | fabrice12345C | 2026-10-21 | BERT-base architecture within DPR component; casing/checkpoint/trained-weight identity not established. |
| GE09 | APPROVE_RECOMMENDED | RAG p. 3 §2.3; p. 4 §2.4 | APPROVED | fabrice12345C | 2026-10-21 | Qualified assertion in sections 2-5 approved; retain all per-claim evidence limitations. |
| GE10 | APPROVE_RECOMMENDED | RAG pp. 4–5 §3.1; pp. 6–7 §4.1 | APPROVED | fabrice12345C | 2026-10-21 | Qualified assertion in sections 2-5 approved; retain all per-claim evidence limitations. |
| GE11 | APPROVE_RECOMMENDED | RAG pp. 4–5 §3.1; p. 6 Table 1/§4.1; p. 17 Appendix B | APPROVED | fabrice12345C | 2026-10-21 | Qualified assertion in sections 2-5 approved; retain all per-claim evidence limitations. |
| GE12 | APPROVE_RECOMMENDED | RAG pp. 4–5 §3.1; p. 6 Table 1/§4.1; p. 17 Appendix B | APPROVED | fabrice12345C | 2026-10-21 | Qualified assertion in sections 2-5 approved; retain all per-claim evidence limitations. |
| GE13 | APPROVE_RECOMMENDED | RAG pp. 4–5 §3.1; p. 6 Table 1/§4.1; p. 17 Appendix B | APPROVED | fabrice12345C | 2026-10-21 | Qualified assertion in sections 2-5 approved; retain all per-claim evidence limitations. |
| GE14 | APPROVE_RECOMMENDED | RAG pp. 4–5 §3.1; p. 6 Table 1/§4.1; p. 17 Appendix B | APPROVED | fabrice12345C | 2026-10-21 | Qualified assertion in sections 2-5 approved; retain all per-claim evidence limitations. |
| GE15 | APPROVE_RECOMMENDED | GraphRAG p. 4 §2.4; p. 5 Figure 3 | APPROVED | fabrice12345C | 2026-10-21 | Qualified assertion in sections 2-5 approved; retain all per-claim evidence limitations. |
| GE16 | APPROVE_RECOMMENDED | GraphRAG p. 3 §1 continuation; p. 5 §2.6; p. 7 §3.3 | APPROVED | fabrice12345C | 2026-10-21 | Map-reduce summarization workflow; no particular software framework identity. |
| GE17 | APPROVE_RECOMMENDED | GraphRAG p. 1 abstract; p. 6 §3.2 | APPROVED | fabrice12345C | 2026-10-21 | Qualified assertion in sections 2-5 approved; retain all per-claim evidence limitations. |
| GE18 | APPROVE_RECOMMENDED | GraphRAG p. 6 §§3.1–3.2; p. 7 §§3.3–3.4 | APPROVED | fabrice12345C | 2026-10-21 | GraphRAG v1 Behind the Tech transcript corpus only; preserve dataset-specific scope. |
| GE19 | APPROVE_RECOMMENDED | GraphRAG p. 6 §§3.1–3.2; p. 7 §§3.3–3.4 | APPROVED | fabrice12345C | 2026-10-21 | MultiHop-RAG news corpus in this experiment; no equivalence to original QA labels. |
| GE20 | APPROVE_RECOMMENDED (component-only condition) | GraphRAG p. 3 §2.1/Figure 2; p. 4 §2.2; p. 6 §§3.1–3.2 | APPROVED | fabrice12345C | 2026-10-21 | Approved for HotPotQA entity-extraction analysis only, not end-to-end QA evaluation; retain evaluation_stage=entity_extraction, COMPONENT_ONLY and sample/chunk-size/gleanings context. |

### Alias sign-off

Record ACCEPT/REJECT/NEEDS_CLARIFICATION as the mapping outcome in your own notes; student decision uses the same approval vocabulary as the claim table. For example, APPROVED on A15 means agreeing to **reject** the proposed Method=Paper merge. Do not approve an excluded equivalence by accident.

| Alias group | AI mapping recommendation | Student decision | Student reviewer | Decision recorded (Europe/Paris) | Student notes / accepted scope |
| --- | --- | --- | --- | --- | --- |
| A01 | ACCEPT (qualified) | APPROVED | fabrice12345C | 2026-10-21 (recorded) | ACCEPT only the qualified mapping and boundaries in section 6. |
| A02 | ACCEPT (qualified) | APPROVED | fabrice12345C | 2026-10-21 (recorded) | ACCEPT only the qualified mapping and boundaries in section 6. |
| A03 | ACCEPT (qualified) | APPROVED | fabrice12345C | 2026-10-21 (recorded) | ACCEPT only the qualified mapping and boundaries in section 6. |
| A04 | ACCEPT (qualified) | APPROVED | fabrice12345C | 2026-10-21 (recorded) | ACCEPT only the qualified mapping and boundaries in section 6. |
| A05 | ACCEPT (qualified) | APPROVED | fabrice12345C | 2026-10-21 (recorded) | ACCEPT only the qualified mapping and boundaries in section 6. |
| A06 | ACCEPT (qualified) | APPROVED | fabrice12345C | 2026-10-21 (recorded) | ACCEPT only the qualified mapping and boundaries in section 6. |
| A07 | ACCEPT (qualified) | APPROVED | fabrice12345C | 2026-10-21 (recorded) | ACCEPT only the qualified mapping and boundaries in section 6. |
| A08 | ACCEPT (qualified) | APPROVED | fabrice12345C | 2026-10-21 (recorded) | ACCEPT only the qualified mapping and boundaries in section 6. |
| A09 | ACCEPT (qualified) | APPROVED | fabrice12345C | 2026-10-21 (recorded) | ACCEPT only the qualified mapping and boundaries in section 6. |
| A10 | ACCEPT (qualified) | APPROVED | fabrice12345C | 2026-10-21 (recorded) | ACCEPT only the qualified mapping and boundaries in section 6. |
| A11 | ACCEPT (qualified) | APPROVED | fabrice12345C | 2026-10-21 (recorded) | ACCEPT only the qualified mapping and boundaries in section 6. |
| A12 | ACCEPT (qualified) | APPROVED | fabrice12345C | 2026-10-21 (recorded) | ACCEPT only the qualified mapping and boundaries in section 6. |
| A13 | ACCEPT (qualified) | APPROVED | fabrice12345C | 2026-10-21 (recorded) | ACCEPT only the qualified mapping and boundaries in section 6. |
| A14 | ACCEPT (qualified) | APPROVED | fabrice12345C | 2026-10-21 (recorded) | ACCEPT only the qualified mapping and boundaries in section 6. |
| A15 | REJECT | APPROVED | fabrice12345C | 2026-10-21 (recorded) | REJECT the proposed equivalence in section 6; no entity merge authorized. |
| A16 | REJECT | APPROVED | fabrice12345C | 2026-10-21 (recorded) | REJECT the proposed equivalence in section 6; no entity merge authorized. |
| A17 | NEEDS_CLARIFICATION | APPROVED | fabrice12345C | 2026-10-21 (recorded) | NEEDS_CLARIFICATION: checkpoint, casing and trained-weight identity unestablished; no merge. |
| A18 | REJECT | APPROVED | fabrice12345C | 2026-10-21 (recorded) | REJECT the proposed equivalence in section 6; no entity merge authorized. |
| A19 | REJECT | APPROVED | fabrice12345C | 2026-10-21 (recorded) | REJECT the proposed equivalence in section 6; no entity merge authorized. |
| A20 | REJECT | APPROVED | fabrice12345C | 2026-10-21 (recorded) | REJECT the proposed equivalence in section 6; no entity merge authorized. |
| A21 | REJECT | APPROVED | fabrice12345C | 2026-10-21 (recorded) | REJECT the proposed equivalence in section 6; no entity merge authorized. |

## 10. Evidence graph and GDS implications

No candidate imports, entity merges, CITES creation or graph status changes were performed. The source snapshot contains proposed identities, not resolved live Entity or Chunk IDs. Source assertions should remain separate Claim records with predicate, paper/version/hash/page, quote and offsets, full support context, qualifiers and review history. Preserve multiple supporting chunks if the context spans chunks; do not replace a context with a short name locator.

Only an explicit real student decision through the project's review process may promote a claim to SOURCE_VERIFIED. A rejected/deferred mapping must not silently canonicalize entities. C03/C09 additionally require approved work-level citation identities before any derived CITES edge; keep `target_work_id`, unspecified cited revision and selected pinned representative distinct. A citation alone does not imply method use; a method-use relation alone does not prove a citation.

After approval, four named Dataset joins can connect DPR and RAG through separately supported claims. Broader architecture/task joins A05/A06 must preserve their abstraction levels. The separate directed work-citation chain would be GraphRAG → RAG → DPR, if later reviewed, materialized and actually queried. No such live path is claimed here.

For the existing proposed GDS projection, form distinct per-paper entity sets from student SOURCE_VERIFIED USES/EVALUATED_ON/ADDRESSES claims and approved alias mappings. Compute Jaccard-weighted, undirected SHARES_ENTITY adjacency; retain supporting claim/entity IDs on both sides, deduplicate pairs, exclude self-loops/zero weights and include isolates. Do not project CITES, MENTIONS, NEXT, PART_OF or hypotheses into this particular similarity graph. Analytical adjacency is derived data, not a scientific source assertion.

**Independently recomputed conditional fixture:** if all 20 qualified candidates and their first fourteen identity mappings are approved, DPR has 6 distinct entities, RAG 8, GraphRAG 6. DPR/RAG share 6 and have a union of 8, yielding weight **0.75**. There are 3 Paper vertices, 1 logical undirected pair, 2 components and GraphRAG is isolated. This is arithmetic on the candidate file, not a Neo4j/GDS result. Defer A05/A06 or exclude a scoped component claim and recompute rather than reuse 0.75 blindly. GDS's stored relationship count may differ from logical undirected pair count; report the actual projection representation.

PageRank would describe navigation prominence in that derived graph, not scientific influence; linked DPR/RAG vertices should be symmetric under symmetric initialization/configuration. Louvain would partition shared-entity structure, with little substantive inference possible from one pair and an isolate. GraphRAG the paper uses **Leiden**; our proposed **Louvain** run is a separate analytics choice. Do not invent edges or widen aliases to eliminate the isolate.

The professor awards **2 points** for a GDS projection plus at least two algorithms, separately from **3 points** for an ML prediction/classification workflow. This review satisfies neither execution criterion. Later evidence must include actual projection inputs/counts, version/configuration, algorithm runs, outputs, timing and interpretation, plus separate ML evidence. Freeze review/alias snapshots and invalidate derived outputs when they change.

## 11. Source review reference and PR #5 submission

The following passage index is retained for teammate review. The student has confirmed inspection and approved all 22 qualified scientific claims in section 9; these passes are no longer outstanding student tasks.

| Personal inspection pass | Exact source passages | Record decisions for |
| --- | --- | --- |
| 1. DPR methods/task | [DPR p. 2 §2](https://arxiv.org/pdf/2004.04906v1#page=2), opening task/extractive definition; [p. 3 §3.1](https://arxiv.org/pdf/2004.04906v1#page=3), Encoders paragraph | GE01, GE02; A05, A06 |
| 2. RAG components/task | [RAG p. 3 §§2.2–2.3](https://arxiv.org/pdf/2005.11401v1#page=3), complete DPR/BERT and BART paragraphs; p. 4 §2.4 continuation and pp. 4–5 §3.1 | GE07–GE10; A05–A08, A15, A17, A18 |
| 3. GraphRAG algorithm/workflow/task | [GraphRAG p. 1 abstract](https://arxiv.org/pdf/2404.16130v1#page=1); p. 3 map-reduce paragraph above §2; [p. 4 §2.4](https://arxiv.org/pdf/2404.16130v1#page=4); p. 5 Figure 3/§2.6 | GE15–GE17; A09–A11, A16, A19, A20 |
| 4. GraphRAG corpora/component | [GraphRAG p. 6 §§3.1–3.2](https://arxiv.org/pdf/2404.16130v1#page=6), both corpus bullets and generated-question description; p. 7 §§3.3–3.4; [p. 3 Figure 2/§2.1](https://arxiv.org/pdf/2404.16130v1#page=3) and p. 4 §2.2 continuation | GE18–GE20; A12–A14, A21. Explicitly accept or defer GE20's component scope. |
| 5. Finish shared-dataset context | [DPR p. 4 §4.2/footnote 6](https://arxiv.org/pdf/2004.04906v1#page=4), p. 5 continuation/Table 1/§5.1, p. 6 Table 2; RAG pp. 4–5 §3.1, p. 6 Table 1, [p. 17 Appendix B](https://arxiv.org/pdf/2005.11401v1#page=17) | GE03–GE06, GE11–GE14; A01–A04. Qualified student decisions are now recorded in section 9. |
| 6. Final citation decisions | [RAG p. 13 ref. [22]](https://arxiv.org/pdf/2005.11401v1#page=13); [GraphRAG p. 13 Lewis et al.](https://arxiv.org/pdf/2404.16130v1#page=13); compare target title-page authors/titles | C03, C09; preserve unspecified target version. Qualified work-level approvals are now recorded in section 9. |

All 22 scientific approvals and the 21 existing alias decisions are recorded in section 9. No missing personal decision remains in the supplied tables. **A17 remains substantively unresolved**: checkpoint, casing and trained-weight identity are not established, and no such merge is authorized. A15-A16 and A18-A21 remain rejected equivalences despite the student's APPROVED endorsement of those rejection recommendations.

This document is prepared for submission through the existing `docs/graph-evidence-review` branch and [PR #5](https://github.com/NeelSabharwal/GraphDBproject-NeelSabharwal-FabriceAfopa/pull/5), targeting `main`. Commit, push and final PR status are reported separately after execution. No new PR, merge or review comment is authorized by this documentation update. Leave PR #5 open for Neel's review.

This Markdown sign-off does not write graph state. Actual review/import mapping, live Neo4j validation, GDS algorithms, ML evaluation and application tests require separate execution evidence. Earlier Work results above are retained reports, not reruns during final submission verification. The rubric's constructive teammate review and merged-contribution requirements are not marked complete by this document.

**Overall status: 22/22 QUALIFIED SCIENTIFIC CLAIMS APPROVED; 21/21 ALIAS RECOMMENDATIONS HAVE RECORDED STUDENT DECISIONS; A17 IDENTITY UNRESOLVED; NO LIVE GRAPH OR APPLICATION VALIDATION CLAIMED.**
