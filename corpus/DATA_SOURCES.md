# Initial corpus — AI Research GraphRAG Assistant

Research date: **2026-10-20, Europe/Paris**. Deadline: **2026-10-23**. Paid-service cost: **€0**. Scope: 10 papers, with a three-paper ingestion shortlist. This is a research handoff, not application implementation or a completed grading criterion.

## Requirements and project alignment

Read the attached `projects_spec.md` and `project_checklist.md`, plus the available `PROJECT_BRIEF.md` and `ARCHITECTURE.md` copies. The professor permits scientific publications for Project 8, requires source documentation and provenance-aware GraphRAG, and separately awards points for an ML prediction/classification workflow. Citation prediction is the project's proposed experiment, not a professor-mandated task. No architecture or project-plan file was changed. The GitHub repository was not available for comparison; its current files remain authoritative over these planning copies.

The brief's three-paper prototype and approximately ten-paper development scope are retained. The architecture's provisional citation-ML gate is **50 verified positives**, including at least 10 in validation and 10 in test. This is a planning threshold, not proof of statistical adequacy.

## Selected sources

All links below pin **v1**, deliberately preserving a fixed historical methods corpus rather than claiming latest-version coverage. Full titles, ordered authors, dates, URLs, license evidence and actual SHA-256 hashes are in `corpus_manifest.json`. Later versions must be treated as a new snapshot, with evidence rechecked.

| Priority | Source and pinned landing page | PDF pages | Selection purpose | Displayed license |
| --- | --- | ---: | --- | --- |
| 1 | [DPR — Karpukhin et al.](https://arxiv.org/abs/2004.04906v1) | 10 | Prototype: dense retrieval | arXiv distribution license |
| 2 | [RAG — Lewis et al.](https://arxiv.org/abs/2005.11401v1) | 18 | Prototype: retrieval plus generation | arXiv distribution license |
| 3 | [GraphRAG — Edge et al.](https://arxiv.org/abs/2404.16130v1) | 15 | Prototype: graph-based corpus summarization | CC BY 4.0 |
| 4 | [REALM — Guu et al.](https://arxiv.org/abs/2002.08909v1) | 12 | Retrieval during pretraining | arXiv distribution license |
| 5 | [FiD — Izacard and Grave](https://arxiv.org/abs/2007.01282v1) | 6 | Compact evidence-fusion comparison | arXiv distribution license |
| 6 | [ColBERT — Khattab and Zaharia](https://arxiv.org/abs/2004.12832v1) | 10 | Late-interaction retrieval | arXiv distribution license |
| 7 | [Self-RAG — Asai et al.](https://arxiv.org/abs/2310.11511v1) | 30 | Retrieval and self-critique | CC BY 4.0 |
| 8 | [HippoRAG — Jiménez Gutiérrez et al.](https://arxiv.org/abs/2405.14831v1) | 28 | Knowledge-graph retrieval and PPR | arXiv distribution license |
| 9 | [G-Retriever — He et al.](https://arxiv.org/abs/2402.07630v1) | 20 | Question answering over textual graphs | arXiv distribution license |
| 10 | [LightRAG — Guo et al.](https://arxiv.org/abs/2410.05779v1) | 16 | Additional graph-assisted retrieval contrast | CC BY-NC-SA 4.0 |

The first three total **43 PDF pages** and cover related but distinct retrieval tasks. Check RAG §2.2, PDF p. 3, for explicit use of DPR; DPR §3.1, p. 3, supplies the underlying method. GraphRAG §2, pp. 3–5, provides a contrasting graph-based evidence pipeline. These support shared-concept questions without treating every mention as method use.

## Verification and reproducibility

All 10 pinned PDFs returned HTTP 200 with PDF content, were downloaded locally, and were processed page-by-page with **pypdf 6.10.0**. All 165 pages yielded nonempty text, and each PDF's extracted text contained the expected arXiv version marker. Nonempty text is not proof of correct reading order. Selected method/reference passages were inspected; DPR p. 3, RAG p. 13 and GraphRAG p. 13 were also visually checked. No application ingestion, entity extraction, model training or benchmark was run.

Notable issues: RAG's v1 landing metadata misspells Aleksandra Piktus as “Aleksandara”; the canonical author list follows the PDF and retains the raw metadata. GraphRAG v1 has eight authors. ColBERT has substantial font-extraction artifacts; defer its ingestion until parser quality is checked. Several PDFs contain ligatures, line-break hyphenation, control characters or figure/table noise. Prototype prose still needs student spot-checking and normalization with provenance preserved.

To transfer: copy this folder into the repository as `corpus/`, retaining companion filenames. All suggested raw-PDF paths are relative to the repository root. Download each `pdf_url` to its `suggested_download_path`, compare its SHA-256, and stop on mismatches. The manifest records downloads performed during this research, not files already present in your checkout. PDFs/full extracted text are **not bundled**. Ignore raw PDFs, page text, caches and generated data in Git.

## Access and reuse

Free access is verified; unrestricted reuse is not universal. The [arXiv distribution license](https://arxiv.org/licenses/nonexclusive-distrib/1.0/) grants rights to arXiv and does not itself establish general downstream redistribution permission. [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) requires attribution and other stated conditions. [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) adds noncommercial and share-alike conditions. Record the displayed paper license, not the code repository's license. Link to papers and keep full PDFs/full text out of the public repository. Embedded third-party material has not been separately audited.

## Citation evidence and the ML decision

`citation_evidence.csv` contains **13 positive links** confirmed by inspecting bibliography entries in the selected source PDFs. It is a verified subset, **not an exhaustive adjacency matrix**. Missing rows mean unknown, not a negative label. Student review remains pending; these research checks do not automatically create `SOURCE_VERIFIED` claims in the application.

The prototype supports **GraphRAG → RAG → DPR**: GraphRAG p. 13, Lewis et al. (2020); RAG p. 13, reference [22]. Citations identify the target *work*, not a specific target arXiv version. The CSV's selected target version is only the corpus representative. Do not assert that a citing author used v1.

Plausible but **unverified** edges include GraphRAG → DPR and Self-RAG → DPR. Do not add them based on topical similarity. HippoRAG references **ColBERTv2** on p. 13, reference [53]; that does not establish a citation to the original ColBERT paper selected here. Keep these identities distinct.

The current evidence does not pass the proposed 50-positive citation-ML gate. See `ML_FEASIBILITY.md` for the 20–30-paper assessment, leakage controls and a proposed Chunk-node classification fallback. No alternative has been implemented.

## Next action and blockers

Start with the three prototype papers and their source-page checks; expand only after that ingestion works. The five development questions and exact passage coordinates are supplied separately, with `gold_answer: null`. Student gold annotation, full parsing QA, complete citation/negative labels, ML feasibility and repository-state verification remain open. No paid API, publisher account or service subscription is required to obtain these PDFs.
