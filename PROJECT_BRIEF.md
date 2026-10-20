# AI Research GraphRAG Assistant

Project 8 — Document-to-Graph GraphRAG Assistant, academic Level 3+.

**Status: PROPOSED. Planning only; no working application or evaluated dataset is claimed.**

The authoritative requirements are [the professor's specification](docs/requirements/projects_spec.md) and [100-point checklist](docs/requirements/project_checklist.md). This brief specializes Project 8 in AI research papers. [PROJECT_PLAN.md](PROJECT_PLAN.md) maps every grading criterion to future work and evidence.

## Problem and users

Students and researchers reading several related AI papers must connect methods, tasks, datasets and citations across documents. A passage may mention a method without establishing that the paper uses it. A generated summary may also hide uncertainty or cite a passage that does not support its conclusion.

The proposed assistant helps students preparing a literature review, researchers exploring a small research area, and instructors examining graph modeling and source-grounded reasoning. It should answer questions, expose supporting passages and graph paths, and clearly label unreviewed extractions and predictions.

## Goals and use cases

- Import a selected collection of scientific PDFs and retain reproducible paper, page and chunk identifiers.
- Extract candidate entities and relations using an LLM; validate their structure and evidence before student review.
- Ask questions using vector retrieval plus bounded Cypher traversal through related papers and concepts.
- Compare papers through shared methods, datasets or tasks, with supporting passages for each association.
- Explore a shortest citation path, related concepts, paper centrality and communities.
- Evaluate a small graph-based citation-link prediction experiment separately from factual question answering.
- Demonstrate a genuine LangGraph tool-calling agent, including successful evidence retrieval and an invalid-output rejection.
- Defend schema, algorithm, index and reliability choices with measured results and documented alternatives.

## Proposed corpus and growth gates

Use English, digitally generated, publicly accessible AI papers centered on retrieval-augmented generation, dense retrieval and graph-assisted retrieval. These form a coherent candidate scope with potentially overlapping concepts. Actual citation links and shared entities must be checked in the selected versions.

| Stage | Target, not achieved count | Proposed selection and exit gate |
| --- | --- | --- |
| Prototype | 3 papers | Start with the three candidates below. Confirm access and license metadata, text/page extraction quality, and a small manually checked evidence sample for each. |
| Development | Approximately 10 papers total | Retain the prototype set and select about seven related papers on retrieval, grounding, graph retrieval and evaluation. Prioritize inspectable PDFs and meaningful cross-paper questions. Freeze a development manifest before tuning. |
| Evaluation | 20–30 papers total, if practical | Expand within the same topic area, subject to student review effort, hardware, extraction cost and ML label feasibility. Freeze versions and a held-out question set. Record actual counts only after ingestion and validation. |

Prototype candidates, with bibliographic identity checked against their arXiv landing pages on 2026-10-19:

1. [Dense Passage Retrieval for Open-Domain Question Answering](https://arxiv.org/abs/2004.04906), Karpukhin et al. — a dense-retrieval anchor.
2. [Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/abs/2005.11401), Lewis et al. — a retrieval-plus-generation anchor.
3. [From Local to Global: A Graph RAG Approach to Query-Focused Summarization](https://arxiv.org/abs/2404.16130), Edge et al. — a graph-oriented comparison candidate.

These are candidate sources, not downloaded, parsed or evaluated project data. Exact PDF versions and reuse permissions remain to be recorded. Free access does not imply permission to redistribute PDFs. Keep downloaded PDFs and generated datasets outside Git; retain a versioned manifest containing source URL, paper identifier, version, license/access note, download date and checksum. Do not add unrelated papers merely to inflate the count or force favorable results.

The 3-paper prototype cannot establish useful ML generalization. Even 20–30 papers may yield too few verified citation links. The ML feasibility gate in [ARCHITECTURE.md](docs/ARCHITECTURE.md) must be evaluated before promising a meaningful experiment. Any expansion beyond the agreed scope requires student approval.

## Example research questions

These are proposed evaluation prompts, not claims that the chosen papers contain the answers:

- Which papers explicitly use a dense retriever, and which merely discuss one?
- Which methods are evaluated on the same dataset, and where does each paper say so?
- How do the selected papers describe retrieval's role in supporting generated answers?
- Is there a directed citation path from paper A to paper B within this corpus?
- Which papers bridge groups of shared concepts, and how does that change when unreviewed claims are excluded?
- Which candidate citation links does the graph model suggest, and which are only hypotheses?
- Does the corpus support a specific comparison, or should the assistant abstain?

## Why a knowledge graph

Vector similarity helps find passages phrased differently from a question. A graph adds explicit identity, typed relationships and reusable joins: paper → validated claim → dataset ← validated claim ← another paper. It can distinguish a mention from an asserted use, aggregate evidence across papers, and return a bounded citation path with its supporting references.

Those benefits depend on extraction quality and entity resolution. A graph can amplify a mistaken merge or unsupported relationship. Hybrid retrieval is therefore a hypothesis to evaluate against vector-only retrieval using the same corpus, generator and evidence budget; superiority is not assumed. Questions needing only one passage may gain little from graph traversal.

## Boundaries and non-goals

The proposed scope is a local academic application: FastAPI/OpenAPI and a demonstration notebook, with a small reviewed corpus and one LangGraph agent. Initial parsing targets readable text PDFs; scanned pages, table reconstruction, equation interpretation and complex figure extraction are deferred unless the corpus proves they are necessary.

The assistant reports what sources state. A reviewer-verified extraction means that a passage supports the recorded claim; it does not establish that the scientific result is independently true. Predicted links remain hypotheses and do not become verified source facts.

Non-goals are a complete literature-search engine, autonomous scientific discovery, automatic benchmarking of competing models, training a foundation model, a production multi-user platform, arbitrary web crawling, unrestricted natural-language-to-Cypher execution, and a custom frontend. No agent teams, queues, separate vector database or orchestration platform are proposed for the initial scope.

## Success evidence and approvals

Success requires a reproducible working system, meaningful tests, evaluated extraction/retrieval/ML behavior, and the collaboration and demonstration evidence required by the professor. Planning coverage alone earns no claimed points. Targets and measures are defined in the plan and architecture; measured failures and limitations must be retained.

Students must approve corpus scope, evidence-review policy, schema and algorithm choices, and ML feasibility criteria before their implementation. On 2026-10-19 the user authorized only local infrastructure and model smoke tests: deadline Friday, October 23, 2026; two students; user as team lead; zero paid APIs/cloud/subscriptions. Hardware and the CPU-only runtime trial are recorded in D13 of [DECISIONS.md](docs/DECISIONS.md). Individual assignments and a future public registry destination remain unconfirmed.
