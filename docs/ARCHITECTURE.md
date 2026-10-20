# Proposed architecture — AI Research GraphRAG Assistant

**Status: infrastructure and initial ingestion implemented; remaining application architecture PROPOSED.** The user authorized local infrastructure on 2026-10-19 and three-paper ingestion on 2026-10-20; see D13–D14 in [DECISIONS.md](DECISIONS.md). The [specification](requirements/projects_spec.md) and [checklist](requirements/project_checklist.md) govern scope. Actual verification is recorded separately from proposed retrieval, agent, GDS analytics and ML behavior.

### Implemented ingestion scope — 2026-10-20

Prompt #5 now authorizes the three-paper ingestion milestone. D14 in the
[decision register](DECISIONS.md) supersedes the older ingestion proposals below
where they differ. `python -m scripts.ingest` verifies the prototype manifest/PDFs,
parses pages with pypdf 6.10.0, records raw/normalized offsets and hashes, and writes
page-bounded character chunks and claims through parameterized UNWIND transactions.
Four identity constraints and four lookup indexes are implemented; vector indexing
and embeddings remain future work. The existing HTTP API remains health-only;
the import is a local operator CLI.

Prompt #5.1 restores independent student semantic review for every SOURCE_VERIFIED
claim, including citations. Automated bibliography checks record
`source_location_status=SOURCE_LOCATED` separately; claims remain EXTRACTED pending
review. Legacy automatic approvals are downgraded without deleting evidence, with
previous metadata retained in review history. A local explicit review action records
a named reviewer, decision, note and time. CITES requires SOURCE_VERIFIED plus approved
human-review metadata; neither quote matching nor status alone suffices. Target version
as cited remains unspecified; the selected Paper is only the corpus representative.

The bounded method sample now locates explicit use passages for BERT (DPR page 3),
BART-large (RAG page 3) and Leiden (GraphRAG page 4), retaining original chunk IDs and
coordinates. A method-specific schema embeds the entity once to avoid inconsistent
copied target names. Exact quotes, typed predicates and pending semantic review remain
mandatory. Import and optional extraction outcomes are separate in CLI reports; see
D15 and INGESTION.md for the exit contract and actual results.

Entity IDs initially include the source paper, kind and normalized surface name.
Cross-paper scientific alias merging needs later review; no topic-similarity citation
inference occurs. Normalized chunks are stored in Neo4j; full raw pages and character
maps are retained in ignored local run artifacts. The pipeline preserves existing
claim reviews on re-import and refuses changed PDF/parser/chunker identities without
a migration. See [INGESTION.md](INGESTION.md) for schema, reproduction and actual results.

### Authorized infrastructure milestone

Deadline: Friday, October 23, 2026; two students; user is team lead; zero paid APIs/cloud/subscriptions. Compose implements Neo4j Community 5.26.32 with checksum-pinned GDS 2.13.2, a Python 3.12 health-only FastAPI service, and Ollama 0.40.6 on CPU. Caps are 4/1/6 GiB RAM (11 GiB total), with container swap disabled, inside the observed 15.30 GiB WSL ceiling. Only localhost:8000 is published. System Python 3.14.4 remains untouched.

For this milestone readiness means authenticated Bolt + the exact GDS version function and reachable Ollama with both selected model tags present, within a 3-second concurrent probe budget. No schema or vector index exists yet, so readiness does not claim either. Model inference is verified separately through bounded explicit smoke commands. Server health and model presence do not prove model quality. Named volumes persist data/logs/model weights; `.env` is ignored and excluded from build context. The historical proposed sections below describe future scope unless explicitly superseded here.

**Verified foundation:** all three containers healthy; Neo4j/GDS 5.26.32/2.13.2, Python/FastAPI 3.12.13/0.115.12 and Ollama 0.40.6; real CPU text/JSON/tool-selection/embedding smoke cases passed. Twelve tests passed with 100% coverage of the current 72 application statements. Detailed timing, memory, licensing and setup limitations are in [INFRASTRUCTURE.md](INFRASTRUCTURE.md); no ingestion, graph schema, LangGraph agent, analytics or ML has been implemented. GDS function/catalog execution is verified, while PageRank/Louvain are only registered, not executed.

## 1. Smallest proposed service boundary

Use Python 3.11+, FastAPI, Pydantic, the official Neo4j Python driver and LangGraph in one application. Ingestion and analytics are scripts using the same application modules. Neo4j holds graph data and chunk vectors. An Ollama service supplies a selected local extraction/generation model and a separate embedding model. Model identities, licenses, digests and hardware requirements remain undecided.

| Compose service | Role and image strategy | Proposed ports and persistence | Health/readiness evidence |
| --- | --- | --- | --- |
| `neo4j` | Neo4j 5.x official base with an exactly matched GDS plugin; document any custom image used to package it | Internal Bolt 7687 and HTTP 7474; localhost bindings only for development; named database volume | Authenticated lightweight query; version and required GDS procedure checks at startup |
| `api` | Custom Python image containing FastAPI, LangGraph and shared ingestion/analytics modules | HTTP 8000; localhost development binding; read-only access to selected PDFs, separate writable artifact directory | `/health/live` checks process; `/health/ready` checks DB, schema/vector index readiness and model availability with timeouts |
| `ollama` | Official image for local inference and embeddings; pinned image and model digests | Internal HTTP 11434; persistent model volume | Server health plus presence of required models; a startup smoke inference validates actual usability |

These are three functional services: storage/graph computation, API/agent orchestration, and model inference. GDS runs inside Neo4j, not as a fabricated fourth service. No separate worker is needed for bounded student imports; scripts handle full batches. Authenticate the import endpoint to satisfy the sensitive-endpoint option in the rubric. A reverse proxy is not needed for this local design.

```mermaid
flowchart LR
    U[Student / Swagger / demo notebook] -->|HTTP localhost:8000| A[FastAPI + LangGraph]
    F[Approved PDF manifest + local PDFs] -->|Authenticated import or CLI batch| A
    A -->|Bolt 7687: templates, graph, vectors| N[Neo4j 5.x + GDS]
    A -->|HTTP 11434: extraction, generation, embeddings| O[Ollama]
    A -->|Evaluation reports and evidence traces| R[Local artifacts]
    N --- V[Persistent database volume]
    O --- W[Persistent model volume]
    U -.->|Optional localhost:7474| N
```

This is a proposal diagram. Later provide editable draw.io diagrams and exported images showing the actual services, ports and flows, with screenshots of the working deployment.

### Version and licensing gate

The professor specifies Neo4j 5.x. The official [GDS compatibility matrix](https://neo4j.com/docs/graph-data-science/current/installation/supported-neo4j-versions/) consulted on 2026-10-19 lists Neo4j 5.26 with GDS 2.13. Treat that release family as a candidate, not a tested patch combination. Before implementation, select supported exact patches, verify plugin/image licenses and platform availability, and record image digests and plugin checksum. Do not pair Neo4j 5.x with an automatically downloaded latest GDS release or silently migrate to Neo4j 2026.x.

Pin Python dependencies and validate Neo4j driver, LangGraph, model integration and GDS procedure compatibility in a small smoke test. Use the Neo4j driver for GDS calls initially, avoiding an extra GDS client dependency. Exercise projection, both algorithms and vector lookup against the selected images. Build the application image for public registry publication without credentials, PDFs, model weights or generated data; record the registry URL and immutable digest only after an actual push and independent pull/run check.

If local inference is unsuitable for available hardware, seek approval for hosted inference and a useful replacement third service, such as Nginx. This is an alternative architecture, not an automatic fallback or a reason to run an unused container.

## 2. PDF ingestion, parsing and extraction

1. **Manifest and access:** approve source URLs and versions; record paper ID, title, authors as metadata, year, license/access note and SHA-256. Initial import accepts manifest IDs from a controlled local directory, not arbitrary URLs or filesystem paths. Enforce file count, size and PDF-type limits.
2. **Page parsing:** propose pypdf for digitally generated text. Preserve raw page text separately from normalized text, use 1-based PDF page numbers, and retain printed page labels when available. Headers, columns, ligatures and hyphenation require sample review. pypdf documents both text-extraction limits and the absence of OCR; see its [text-extraction guide](https://pypdf.readthedocs.io/en/stable/user/extract-text.html). Reject or flag pages with inadequate text instead of inventing content. Evaluate a layout-aware alternative only if samples fail.
3. **Chunking:** start with page-bounded paragraph chunks targeting about 500 tokens with about 75 tokens of overlap, clipped to the selected model's context limit. These are tuning proposals. Never silently concatenate pages. Store normalized-page character offsets and raw-to-normalized mapping, PDF hash, section if reliable, tokenizer/chunker version and text hash. `NEXT` preserves reading order. Reference-section chunks are tagged and excluded from semantic-use extraction while remaining available for citation validation.
4. **Structured extraction:** send chunk text as untrusted data to the selected LLM. Require a Pydantic-compatible schema containing entity spans, candidate subject/predicate/object, verbatim supporting quote, offsets, qualifiers and an optional self-reported confidence in [0,1]. Allow only approved entity kinds and predicate/domain/range combinations. Preserve model digest, prompt version, run ID and original structured response for audit.
5. **Validation:** check output schema, quote/offset agreement against stored normalized text, existing endpoints, valid page/chunk references and predicate types. Reject malformed or unsupported outputs into a review artifact; permit at most one formatting retry. Exact quote matching is evidence-location validation, not proof that the quote entails the claim. Retain negation and attribution; do not turn related-work mentions into a paper's own method use.
6. **Resolution and review:** normalize whitespace and case, but merge scientific entities only through reviewed alias mappings. Preserve surface names and ambiguous candidates. A student checks the supporting page and relation interpretation before promoting a claim to `SOURCE_VERIFIED`; store reviewer and timestamp. Contradictory claims remain separate and visible.
7. **Load and reproducibility:** batch parameterized writes using `UNWIND` and the Neo4j driver, with deterministic IDs and bounded transactions. Re-importing identical PDF/extractor versions should not duplicate nodes. New PDF or extraction versions create separately traceable records; derived relations and projections are rebuilt for a declared corpus snapshot. Checkpoints record success/failure per paper so partial imports can be resumed. Downloaded/generated files stay ignored; manifests, prompts and redistributable small test fixtures are tracked.

## 3. Graph model and provenance

### Proposed node labels and properties

| Label | Meaning | Main proposed properties |
| --- | --- | --- |
| `Paper` | One specific paper version | `id`, `work_id`, `title`, `authors`, `year`, `source_url`, `source_version`, `pdf_sha256`, `license_note`, `parse_status` |
| `Chunk` | Text span within one PDF page | `id`, `page`, `page_label`, `ordinal`, `start_char`, `end_char`, `text`, `text_sha256`, `section`, `parser_version`, `chunker_version`, `embedding`, `embedding_model` |
| `Entity` | Reusable scientific concept | `id`, `canonical_name`, `normalized_name`, `kind` in Method/Dataset/Task/Topic, `aliases`, `resolution_status` |
| `Topic` | Additional label on topic-kind Entity nodes | Same Entity identity; supports topic exploration without duplicating concepts |
| `Claim` | A source-specific proposed assertion | `id`, `predicate`, `status`, `origin`, `llm_confidence`, `validation_checks`, `qualifiers_json`, `model_id`, `prompt_version`, `run_id`, `reviewer`, `reviewed_at` |

`validation_checks` is a list of check identifiers; structured qualifiers are serialized JSON, not an unsupported nested Neo4j property map. Null values mean unknown, not zero. Confidence is a model score, not a calibrated probability. Scientific performance tables are outside initial extraction scope; comparative claims require explicit conditions and student review.

Proposed claim states are `EXTRACTED` (structurally valid, source-located, not semantically reviewed), `SOURCE_VERIFIED` (a named student confirmed that the cited source supports the assertion), `REJECTED` (failed review, excluded from retrieval) and `HYPOTHESIS` (a model suggestion, excluded from factual retrieval). `origin` records LLM/manual/ML independently of review status. Preserve transitions and reasons in versioned review records. Neither a high confidence score nor a successful quote match automatically promotes a claim. Stored page text is a source artifact with parsing-quality checks, not an LLM assertion; a citation to it must still support the answer's meaning.

### Directed relationships

| Pattern | Meaning and properties |
| --- | --- |
| `(Chunk)-[:PART_OF]->(Paper)` | Exactly one parent version per chunk; deterministic document structure |
| `(Chunk)-[:NEXT]->(Chunk)` | Next chunk within the same paper version; no cross-paper links |
| `(Chunk)-[:MENTIONS]->(Entity)` | Entity surface mention; span offsets, surface form, validation status; not evidence that a paper uses a method |
| `(Claim)-[:SUBJECT]->(Paper or Entity)` | Exactly one assertion subject, validated by predicate domain |
| `(Claim)-[:OBJECT]->(Paper or Entity)` | Exactly one assertion object, validated by predicate range |
| `(Claim)-[:SUPPORTED_BY]->(Chunk)` | Quote, start/end offsets and quote hash; one or more supports required for extracted/verified claims |
| `(Paper)-[:CITES]->(Paper)` | Derived only from source-verified citation claims; `claim_ids`, `snapshot_id`; excludes outside-corpus targets initially |

Initial predicates: `USES` (Paper → Method), `EVALUATED_ON` (Paper or Method → Dataset), `ADDRESSES` (Paper or Method → Task/Topic), `CITES` (Paper → Paper). Expand only for a demonstrated question. `EVALUATED_ON` claims retain the paper context; using the same dataset does not establish comparable evaluation settings.

```mermaid
flowchart LR
    C[Chunk] -->|PART_OF| P[Paper]
    C -->|NEXT| C2[Chunk]
    C -->|MENTIONS| E[Entity: Method / Dataset / Task / Topic]
    Q[Claim: predicate + status + origin] -->|SUBJECT| P
    Q -->|OBJECT| E
    Q -->|SUPPORTED_BY: quote + offsets| C
    Q2[Claim: CITES] -->|SUBJECT| P
    Q2 -->|OBJECT| P2[Paper]
    Q2 -->|SUPPORTED_BY| C
    P -->|CITES: verified claim_ids| P2
```

The diagram illustrates common paths; the relationship table is authoritative for allowed endpoints. A hypothesis may be represented as a `Claim` with `origin=ML`, `status=HYPOTHESIS`, model/run identifiers and prediction score, but no invented `SUPPORTED_BY` edge. Prefer an evaluation artifact initially; persist hypotheses only if needed for the demo, isolated from default retrieval and projections.

### Constraints and indexes

- Uniqueness constraints on `Paper.id`, `Chunk.id`, `Entity.id` and `Claim.id` prevent duplicate identities; at least two are required by the rubric. Record actual DDL and demonstrate duplicate rejection later.
- ID constraints provide backing lookup indexes; do not add redundant indexes on the same IDs.
- A composite range index on `Entity(kind, normalized_name)` supports candidate resolution. Consider `Paper(year)` only if measured filtering warrants it.
- A vector index on `Chunk.embedding` supports semantic seeds. Pin embedding model/digest, dimension and cosine metric; a model change requires re-embedding and rebuilding the index. The [Neo4j vector-search documentation](https://neo4j.com/docs/cypher-manual/5/indexes/semantic-indexes/vector-indexes/) provides the version-specific API; verify the selected 5.x procedure in the smoke test.
- Validate required properties, claim cardinality, predicate endpoint types and evidence presence in ingestion and integration tests. Uniqueness constraints alone cannot enforce all graph semantics; do not assume Enterprise-only constraint features are available.
- Use `EXPLAIN` and safe read-query `PROFILE` on representative data to justify indexes. An index existing is not evidence that the intended query uses it.

### Modeling tradeoffs

Claim nodes add hops and review work compared with storing every extracted relation directly as an edge. They preserve source-specific evidence, qualifiers, contradictions and review status without overwriting a relation shared by several papers. Only verified citations get a derived edge because shortest paths benefit from it; it remains rebuildable from claim IDs.

Entity nodes permit cross-paper joins and alias resolution; storing method/dataset names as Paper string arrays would be simpler but obscure identity and evidence. Entity `kind` avoids many narrowly defined labels; a Topic secondary label supports Project 8's exploration endpoint. Authors stay metadata initially because author-network questions are out of scope. Page nodes are unnecessary while chunks stay within pages. A generic `RELATED_TO` graph is rejected because it hides what the source actually asserts. Students must compare this proposal against a separately saved generic AI schema and defend their final differences; this AI-written proposal is not itself evidence of that exercise.

## 4. Hybrid retrieval and agent behavior

### Retrieval contract

Embed a question with the same model used for chunks. Retrieve a bounded top-k vector seed set (initial k=8, tuning on development questions only). Resolve entity candidates from seed mentions and exact aliases, ask for clarification on ambiguous identities, and traverse supported claims to additional chunks/papers within a small hop and result budget. Default graph expansion uses `SOURCE_VERIFIED` claims; an explicit exploratory mode can include `EXTRACTED` claims with visible labels. Deduplicate by chunk ID and preserve all supporting claim IDs.

Combine vector candidates and graph-expansion candidates with reciprocal-rank fusion, with stable tie-breaking. Graph candidate order uses verified-support count then shortest connection distance; it is not a scientific truth score. Cap the final context to the same token budget as the vector-only baseline. Each answer statement references returned evidence IDs. A citation includes paper title/ID, version/hash, PDF page, chunk ID and quote/offsets; graph paths include their claim IDs and statuses. A valid URL alone is not a valid citation.

### Genuine single-agent LangGraph design

Use a typed `StateGraph` with state fields: question, resolved IDs, messages/tool requests, remaining step/time budgets, retrieved evidence IDs, graph paths, validation failures, tool-event trace, answer and abstention reason. The model chooses among typed tools such as `search_chunks`, `resolve_entity`, `expand_evidence`, `find_citation_path`, `rank_related_papers` and `get_source_excerpt`. Tools return structured results with status, IDs and limits applied.

The framework supports tool-calling loops and conditional transitions; see the official [LangGraph workflows and agents guide](https://docs.langchain.com/oss/python/langgraph/workflows-agents). The bounded workflow below is this project's proposed design, to be verified against pinned package versions.

```mermaid
flowchart TD
    S[Validate question + initialize state] --> A[Model selects tool or proposes answer]
    A -->|Tool call| V[Validate tool name + arguments]
    V -->|Valid| T[Execute bounded read-only tool]
    V -->|Invalid, retry budget remains| A
    T --> E[Accumulate evidence + tool trace]
    E -->|More evidence needed, budget remains| A
    A -->|Answer candidate| C[Validate structured answer + citation support]
    C -->|Supported| F[Return answer + evidence + trace]
    C -->|Repairable, budget remains| A
    C -->|Unsupported or budget exhausted| X[Abstain / return partial supported answer]
    V -->|Unsafe or budget exhausted| X
```

Propose at most six tool calls, one malformed-output retry and a configurable wall-clock timeout. The conditional loop must be demonstrated with an actual multi-tool run. Record tool name, validated arguments, timing, query-template ID, returned evidence/paths and outcome. Expose that operational trace rather than private model reasoning. Require a structured answer with supported statements, citations, explicit unverified claims/hypotheses and limitations. An LLM judgment of entailment can flag issues but cannot promote a source claim to verified status.

### Read-only Cypher and hallucination guardrails

The model selects a query-template ID and typed parameters; it never supplies executable Cypher. Use a fixed registry of reviewed, parameterized read queries and explicitly allowed read/stream procedures. Reject raw Cypher, unknown tool/template names, mutation attempts, invalid IDs, unexpected parameter keys, unlimited depths and oversized limits. Select bounded-depth query variants server-side instead of interpolating user strings into syntax. Validate the generated query plan and bound values before execution, then check result and citation schemas. Demonstrate rejection of a model-produced write attempt.

Use read transactions, query timeouts, row limits, pagination and API request budgets. Driver read routing alone is not a database authorization boundary. If the selected Neo4j edition provides suitable roles, use a restricted query principal; otherwise enforce read-only query capabilities in the application, keep Bolt private and document the Community-edition limitation. Separate ingestion functions/credentials from agent tools; no tool can invoke import, GDS projection/write operations, arbitrary procedures, shell commands or external URLs. Only named GDS streaming procedures may be invoked through controlled analytical tools against an already prepared snapshot.

Authenticate `POST /api/corpus/import` with a secret supplied through environment configuration. Fail closed when the secret is absent, redact it from logs, and test missing/invalid/valid credentials. TLS and broader user management are future deployment concerns, not needed for a localhost demonstration.

Treat PDF text and retrieved quotations as data, including embedded instructions. Never execute document instructions. Enforce output evidence membership and source-status checks in code; review a sample of semantic entailment manually. Preserve conflicts, answer only within the corpus, and abstain when evidence is insufficient. A match between quotation and page text verifies a location; human source verification verifies that the source states the assertion; neither proves independent scientific truth.

## 5. FastAPI contract and graph-query evidence

All paths below are PROPOSED. Pydantic request/response models must enforce lengths, IDs, enums, limits and response provenance. `/docs` exposes the actual OpenAPI schema once implemented.

| Endpoint | Purpose and planned graph behavior | Advanced / algorithm evidence |
| --- | --- | --- |
| `POST /api/corpus/import` | Authenticated, size-bounded import of selected manifest IDs; return per-paper results and failures; full batches may use CLI | Ingestion, not counted as an advanced query |
| `GET /api/ask?q=...` | LangGraph hybrid retrieval, answer, citations and tool trace | Agent; do not rely on it alone for the three advanced-query requirement |
| `GET /api/topics/{id}/graph?depth=2` | Bounded claim traversal to papers/methods/datasets; return evidence subgraph and aggregate distinct-paper support | Advanced query 1: complex patterns, `WITH`, bounded subqueries and aggregation |
| `GET /api/papers/{id}/paths?target_id=...&max_hops=4` | One shortest directed citation path using verified `CITES`, each edge expanded to source evidence; no-path is an explicit result | Advanced query 2; pathfinding endpoint 1 |
| `GET /api/papers/centrality?limit=10` | Stream PageRank over the prepared paper projection; return rank, snapshot and algorithm parameters, with shared-entity explanations | Advanced query 3; GDS endpoint 2 |
| `GET /api/papers/communities?limit=10` | Stream Louvain communities on the same projection; return members and shared-entity summaries | Additional advanced GDS endpoint; demonstrates second algorithm |
| `GET /health/live`, `GET /health/ready` | Process and dependency readiness | Operational endpoints; not counted as domain use cases |

Stream GDS results for this small corpus using a bounded configured concurrency, not a projection rebuild per request. Projection refresh is an explicit ingestion/analytics step. Missing/stale projections yield an actionable 503, not silently recomputed or fabricated ranks. Verify actual pathfinding and GDS execution in endpoint tests; returning a hardcoded or unlabeled cached score is insufficient.

Use parameterized `UNWIND` for batch lookup of supporting claim IDs, `WITH` for early deduplication, correlated subqueries for bounded evidence retrieval and aggregation for distinct paper counts. Avoid disconnected `MATCH` patterns and Cartesian products. The citation-path search operates only on directed verified citations and explicitly caps hops; concept paths use the claim model and are not mislabeled citation paths. Proposed limits: depth ≤3 for concept expansion, citation hops ≤6, page size ≤50 and a maximum returned subgraph size. Document truncation in responses.

Return 401/403 for authentication/authorization failure, 404 for missing IDs, 409 for conflicting imports/snapshots, 413 for excessive input, 422 for invalid fields, 429 for budgets, and 503/504 for unavailable dependencies/timeouts. A valid but disconnected path request returns an empty path with reason; lack of evidence is an abstention outcome, not a server exception. Log request IDs and safe error details.

## 6. GDS projection and two algorithms

Build a named, versioned in-memory projection containing all selected `Paper` nodes and a derived undirected `SHARES_ENTITY` adjacency. For each paper, form the set of entities attached through `SOURCE_VERIFIED` USES/EVALUATED_ON/ADDRESSES claims. Connect distinct papers when these sets overlap; weight = Jaccard intersection/union, exclude zero weights and self-loops, include isolated papers explicitly. Deduplicate each unordered pair before projecting it as undirected so reciprocal entries are not accidentally doubled. Retain contributing entity/claim IDs in a separate explanation mapping.

This projection answers corpus similarity questions without allowing document structure (`NEXT`, `PART_OF`) or unreviewed hypotheses to dominate graph metrics. It may be disconnected, and is not a citation or causal graph. Estimate GDS memory before creation, record node/relationship counts and weight distribution, cap resource use, and drop obsolete projections after refresh. Snapshot identity includes corpus and review-state hashes; any verification change invalidates dependent results.

- **Weighted PageRank:** propose ranking structurally well-connected papers as corpus navigation entry points. Document damping, iterations and convergence; a default damping candidate is 0.85. On this undirected graph it may largely track weighted degree, so compare with a degree baseline and do not call the score scientific impact. Algorithm reference: [GDS PageRank](https://neo4j.com/docs/graph-data-science/current/algorithms/page-rank/).
- **Weighted Louvain:** propose grouping papers by shared scientific concepts. Inspect modularity, component structure and representative shared entities; test stability across repeated runs where the chosen version permits seed/configuration controls. Small groups may be unstable, and community IDs are arbitrary. Algorithm reference: [GDS Louvain](https://neo4j.com/docs/graph-data-science/current/algorithms/louvain/).

Use streaming results initially. Keep algorithm configuration, projection hash, timestamps and runtime with every report. A tiny fixture can verify behavior; actual corpus results are required for the academic demonstration. Do not claim communities or high-impact papers before running the algorithms.

## 7. Measurable graph-based ML experiment

**PROPOSED task:** reconstruct held-out, source-verified directed citation links among papers in the frozen corpus. This is an educational link-prediction experiment, not evidence that a paper should cite another or that a predicted relationship is true.

1. Establish ground truth from reviewed reference sections and resolved in-corpus paper IDs. Incomplete or unreadable reference lists cannot supply verified negative labels. Record the label-review procedure and uncertain cases.
2. At the development gate, inspect label count and graph connectivity. A provisional minimum is 50 verified positive links, permitting at least 10 positives in each validation and test set under a 60/20/20 split. This is a feasibility threshold, not a statistical sufficiency claim. Three or ten papers are unlikely to establish meaningful results; 20–30 may still fail this gate.
3. Freeze a deterministic directed-pair split. Remove validation/test edges before computing **any** topology features, projections or degree/PageRank scores. Collapse duplicate paper versions for the experiment and prevent the same pair from appearing in several partitions. Keep all node identities for a declared transductive task. Log disconnected/cold-node cases rather than dropping difficult cases after evaluation.
4. From the training citation graph compute source out-degree, target in-degree, common-neighbor counts on a declared undirected view, and endpoint PageRank using a separate GDS projection. No target `CITES` edges, citation Claim nodes, bibliography text, full-graph analytics or evidence IDs can enter the feature pipeline. A separate read dataset of training edges is the leakage boundary. Pair absence from the whole verified graph is used only to construct labels, never as a feature.
5. Fit standardized logistic regression in scikit-learn with fixed seeds. Compare with a constant prevalence baseline and a simple preferential-attachment ranking. This is graph-based ML because its learned features derive from graph topology and GDS; PageRank alone is not an ML workflow. A GDS ML pipeline is an alternative if the professor requires it, but adds version-sensitive machinery.
6. Use non-self candidate pairs within the corpus. Verified absent citations are negatives for this closed-corpus task; sample training negatives at a recorded ratio and evaluate on the remaining eligible held-out candidate pairs with their natural class distribution. Publish split IDs, counts, class balance and seeds. Tune only on validation data.
7. Report average precision/PR-AUC, ROC-AUC when both classes exist, precision@k and recall@k, plus baseline comparisons, per-split counts and variability across predeclared repeated splits. Treat small-sample uncertainty explicitly; never imply independent observations from overlapping graph folds. Recompute all features within every split.
8. Store predictions with model version, score and `HYPOTHESIS` status in a report; do not merge them into verified citation edges or use them to answer source-fact questions. Keep training artifacts separate from serving projections.

If the label gate fails, report the ML criterion as unverified and request approval to expand the corpus or choose a different reviewed-label task. Do not manufacture labels or use synthetic accuracy to claim compliance. A completed, reproducible experiment with honest weak performance is more defensible than an unsupported success claim.

## 8. Tests, benchmarking and evaluation

### Automated verification proposal

- Unit tests: page/chunk provenance, quote alignment, stable IDs, alias ambiguity, extraction validation, evidence status transitions, token/depth budgets and ranking deduplication.
- API tests: all domain endpoints, response models, status codes, import authentication, disconnected paths, invalid tool output, prompt injection and cited-evidence membership.
- Neo4j integration tests: actual connectivity, constraint rejection, idempotent import, directed paths, complex patterns/aggregations, vector index retrieval and read-query boundaries. Use a dedicated fixture database, never destructive tests on a student's corpus.
- GDS/ML tests: projection node/edge/weight checks, algorithm invariants, disconnected fixtures, absent held-out edges, no full-graph features, split disjointness and independently recomputed metrics.
- Container tests: healthy startup, authenticated database query, API live/ready checks and dependency failure behavior. Verify Ollama model readiness separately from process liveness.
- CI: lint and deterministic unit/API/integration tests with coverage artifacts; model responses mocked or recorded for deterministic CI and explicitly labeled. A separately invoked real-model smoke/evaluation run is required before release. `make test` must run Cypher/integration tests or provision documented test services; unavailable required dependencies must not be reported as a passing full suite.

Target the professor's pylint ≥9.5/10 and test coverage ≥60%; retain terminal/XML/HTML coverage evidence and actual exit codes. Apply meaningful behavior tests rather than implementation mirrors. Do not exclude difficult modules simply to inflate coverage. The specification links [required pylint rules](https://gist.github.com/bdallard/f74fe36835b6f0510e8d30bc7ee05023); the linked content could not be retrieved during planning and must be inspected before creating `.pylintrc`.

### Evaluation design and proposed acceptance targets

All counts and thresholds below are proposals, not measured outcomes. Students should approve them before evaluation; freeze them before opening held-out results.

| Area | Proposed sample and measurement | Proposed decision rule |
| --- | --- | --- |
| Extraction | About 100 manually annotated claim opportunities across at least 5 papers, including negatives; compare entities/relations to annotations and audit page/quote alignment | Report precision/recall/F1 and error taxonomy; target relation precision ≥0.85; require exact valid provenance for every accepted claim; small prototype checks are not the final evaluation |
| Retrieval and answers | Target 30 held-out questions: 10 single-source, 10 cross-paper/multi-hop, 5 unsupported, 5 adversarial; keep development questions separate | Compare vector-only and hybrid using the same model, seed corpus, token budget and generator; report recall@k, MRR, citation correctness, answer support and abstention |
| Reliability | Manual evidence-based marking plus automatic schema/citation checks; two students independently review a subset and resolve disagreements | Target ≥90% source-supported answer statements on answerable questions; no fabricated source IDs; report each unsupported/adversarial outcome rather than hide failures in an average |
| Agent behavior | Successful real multi-tool trace and invalid/unsafe output case, including loop-limit behavior | Evidence shows conditional routing, actual tools and validation; a single LLM call or canned trace does not pass |
| GDS | Corpus run plus known-topology fixture; degree comparison and community inspection | Document valid projection, interpretation and limits; no required claim of novel scientific findings |
| ML | Frozen labels/splits and the workflow above | Complete leakage-controlled experiment and baseline comparison; report whether it improves rather than require a fabricated improvement |

Gold annotations are made from papers, not copied from the extractor's outputs without review. Questions and references are frozen before final testing; do not tune on test answers. Report missing or excluded cases and the reason. Preserve consented, license-compatible short evidence snippets in evaluation fixtures; raw PDFs remain local.

### Latency and reproducibility

Benchmark the topic, path and centrality queries separately from embedding and generation. On the same frozen corpus/hardware, run a proposed 5 warmups followed by 30 measured requests per query/configuration; report cold-start separately, p50/p95, failures, returned rows, database hits and GDS projection/algorithm times. Record concurrency (initially 1), seeds, resource limits, index state and cache conditions. Compare an unindexed lookup against the justified index and an unbounded-pattern baseline against the bounded rewrite on safe bounded test data; retain identical expected results and `EXPLAIN`/`PROFILE` evidence. Never remove identity constraints merely to manufacture a faster comparison.

Provisional budget: p95 under 1 second for bounded non-LLM graph endpoints on the evaluated corpus; propose an end-to-end agent budget after a real local-model hardware smoke test. If targets fail, document observations and optimize without changing the test corpus secretly. Report measured node/edge/chunk counts only after a recorded run.

Reproduction artifacts should include manifest/PDF hashes, parser/chunker and prompt versions, reviewed alias/label files, model digests, schema version, locked dependency versions, container digests, projection/split definitions, commands, seed and machine specifications. Deterministic fixtures support repeatable CI; live LLM output may vary even with low temperature, so retain responses and provenance for audit. Live demonstration must include fresh execution, not only saved outputs.
