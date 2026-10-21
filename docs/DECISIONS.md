# Proposed decision register

The D01–D12 entries preserve the original **PROPOSED** design. D13 supersedes conflicting budget, scheduling and runtime assumptions; D14 records the subsequent ingestion authorization and explicit bibliography-policy approval. The professor's [specification](requirements/projects_spec.md) and [checklist](requirements/project_checklist.md) remain authoritative. Record approval/rejection, date, participants and supporting evidence when a decision is resolved; update [ARCHITECTURE.md](ARCHITECTURE.md) and [PROJECT_PLAN.md](../PROJECT_PLAN.md) together.

## D21 — Complete application integration and bounded paper retrieval, prompt #6.3

- **Status/authority:** IMPLEMENTED in the working tree under the explicit PR #4
  correction request. No commit/push; deadline October 23, 2026 and zero-cost policy
  unchanged. Pushed-commit verification remains pending the student's commit/push.
- **Completeness:** HEAD `bca43ca` includes the agent but omits seven required
  integration-file changes; three planning/decision updates also remain uncommitted.
  The old running image matches the working tree for main/config/lockfile hashes,
  explaining why local checks passed despite the incomplete commit. Retain all
  missing changes together; expose the selection-retry bound through the same
  validated environment/Compose configuration as the other agent budgets.
- **Retrieval choice:** paper-specific requests use an indexed Paper ID lookup,
  bounded incoming PART_OF traversal and exact cosine ranking of eligible vectors.
  Enumerate at most 257 Chunk rows; reject above 256 without scoring or silently
  truncating. This avoids losing the paper behind 64 better global ANN candidates.
  The function is available in the observed Neo4j 5.26.32 and documented since 5.18
  in the [Neo4j 5 vector-function manual](https://neo4j.com/docs/cypher-manual/5/functions/vector/).
  Unfiltered searches retain the existing approximate global top-64 approach.
- **Alternatives/drawbacks:** raising global ANN candidates still cannot guarantee
  paper recall; unlimited exact search can consume unbounded resources; separate
  per-paper indexes add administration. A fixed 256-row cap fits the current small
  corpus but rejects larger papers. Ranking covers only eligible pinned vectors,
  not stale/missing embeddings, semantic relevance or complete scientific answers.
  The Paper index hint and query timeout fail closed if the required index is absent.
- **Scientific joins:** require a different target Paper, retaining both approval
  gates and exact supporting-source checks. Tests use clearly synthetic review
  metadata with cleanup, never real student approvals or alias merges.
- **Student questions:** inspect answer usefulness and pending claims separately;
  reconsider the paper-size bound only with measured need. No architecture expansion,
  model change, GDS execution or ML work is authorized by this correction.

## D20 — Paper direction and extractive answers, prompt #6.2

- **Status/authority:** IMPLEMENTED within the authorized grounding correction;
  deadline October 23, 2026, zero paid services. Same model, services and LangGraph.
- **Paper identities:** a fixed read returns at most 65 Paper identity rows; more than
  64 rejects resolution rather than silently hiding ambiguous candidates. Existing
  aliases are accepted as identity metadata. The current three nodes have no aliases,
  so conservative title initialisms and explicit title phrases supply names such as
  DPR, RAG and Graph RAG. Names/IDs are exact after case/punctuation normalization.
  Ambiguous and unsupported endpoint names are rejected, independently on each side.
  No scientific Entity aliases, node merges or review metadata are changed.
- **Direction:** a preparation node resolves explicit `from X to Y`, standalone
  `X to Y`, and directed arrows. A directionless `between` request is rejected.
  Resolved IDs constrain both model decoding and runtime validation; vector retrieval
  cannot substitute a different endpoint. Discovery questions retain model selection.
  The actual path still comes only from the approved directed Cypher tool.
- **Grounding:** one short Qwen pass selects up to three passage IDs from at most 12
  lexical candidates in explicitly read evidence. Returned statement text is the
  exact selected quote, not a separately generated paraphrase. Generic matches with
  fewer than two query-term overlaps are omitted; duplicate passages, high token
  overlap, and selections adding no new query aspect are omitted. Unknown passage
  IDs, altered source text, forged coordinates and unsupported paraphrases fail closed.
- **Stopping:** ordinary source questions search once when hits exist, read at most
  two chunks, then route to generation without another FINISH inference. Named
  single-paper searches are filtered to that Paper ID. Graph expansion is available
  only for explicit compare/across/shared/common requests; citation questions use
  the path tool. Cross-paper/discovery requests retain bounded conditional loops.
- **Alternatives:** another LLM verifier adds CPU cost; unconstrained paraphrases
  previously outgrew their quotations; fixed question-to-answer mappings would leak
  expected answers and remove model choice. The new approach chooses source text,
  not answers embedded in code or evaluation labels.
- **Drawbacks:** lexical overlap does not establish entailment, completeness or
  scientific truth. English morphology and sentence splitting are approximate;
  550-character contiguous pieces may cut long sentences. A small catalog/strict
  name grammar can reject valid but unfamiliar phrasings. Title abbreviations may
  collide; these fail rather than guess. Extraction can omit useful explanations.
  Cross-paper intent detection is conservative and may miss implicit comparisons.
- **Student review:** every selected passage still requires manual relevance review.
  SOURCE_LOCATED remains separate from SOURCE_VERIFIED; C03/C09 remain pending.
  Measured tests and live outcomes are recorded in [AGENT.md](AGENT.md).

## D19 — Schema-constrained action selection, prompt #6.1

- **Authority/status:** authorized reliability correction on `feat/agent-evidence`;
  IMPLEMENTED, with measured outcomes in [AGENT.md](AGENT.md). Deadline remains
  October 23, 2026 and budget remains zero. No new model or service is introduced.
- **Decision:** retain the LangGraph select/execute/generate/validate graph and the
  four read tools. Qwen emits a JSON-schema-constrained action, independently checked
  by a Pydantic discriminated union. An explicit FINISH replaces absent native calls.
  Each turn's schema permits only actions with discovered source IDs and enumerates
  those IDs. Runtime membership checks also reject fabricated names or identities.
  State validation requires an actual nonempty source read before FINISH; citation
  questions also require a path attempt. When multiple chunks were discovered, two
  distinct source reads are required before FINISH or factual generation. This small
  coverage gate does not establish semantic sufficiency.
  Unavailable paths abstain without generation.
  Repeated identical normalized searches (including top-k-only changes) and duplicate
  excerpt reads are rejected. One corrective retry is shared across the request,
  bounded by validated settings and the existing overall deadline.
- **Answer correction:** the live intermediate Q04 reached source evidence but failed
  exact citation validation. Keep that validator and constrain answer decoding to
  per-chunk exact source quote choices. Sentence spans longer than 300 characters are
  split into contiguous pieces without normalization or rewriting. This prevents
  copied-quote corruption without treating generated interpretations as verified.
  Repeated expansion of the same paper is excluded after its first attempt.
- **Alternatives:** native tool calls failed on saved Q01/Q08 traces. A deterministic
  question-to-tool chain would remove model direction. A new model/provider or extra
  service is outside scope. Schema-constrained local decoding preserves student-
  defensible orchestration without expanding the read capability.
- **Drawbacks:** syntax and source-read gates cannot establish semantic completeness.
  A valid exact quote can still accompany an incomplete or mistaken interpretation.
  CPU inference may reach deadlines; near-duplicate search paraphrases are limited
  by the call budget rather than an unvalidated semantic duplicate detector.
  Two reads can increase latency or include a less relevant chunk. Sentence splitting
  can fragment mathematical text or abbreviations; semantic interpretation still
  requires review, even when a quote is an exact source substring.
- **Verification policy:** coordinate/quote validation is separate from human approval.
  The synthetic Q15 page-999 output is tested against the actual DPR source without
  changing PDFs, gold or graph properties. No C03/C09 approval is supplied.
- **Remaining student decisions:** review actual answer usefulness/latency and
  independently review pending graph claims. Neither is inferred from passing tests.

## D18 — Bounded local retrieval and LangGraph, prompt #6

- **Authority:** implement embeddings, four read tools and `/api/ask` on
  `feat/agent-evidence`, using only the existing three papers and local models.
  No claim approval, extraction redesign, corpus expansion, GDS or ML training.
- **Decision:** use pinned Nomic v1.5 768-dimensional cosine embeddings in a Neo4j
  vector index. Record model/digest, input hash and search-prefix policy on each
  Chunk. Preparation is an idempotent operator CLI, separate from agent capabilities.
  Model/index incompatibility fails closed and requires an explicit migration.
- **Agent:** LangGraph 0.6.7 with compatible pinned LangChain Core 0.3.76; direct
  Ollama HTTP calls avoid an extra provider adapter. Native structured tool calls
  choose among semantic search, source reading, directed citation paths and one-hop
  reviewed scientific evidence expansion. Conditional loops have call, character,
  query, inference and whole-request budgets; one concurrent CPU workflow.
- **Retrieval:** bounded vector candidates plus model-selected graph expansion, with
  chunk-ID deduplication. Defer rank fusion/learned reranking until reviewed graph
  evidence exists and a controlled comparison justifies it. Search returns metadata;
  explicit excerpt reads select answer context. No superiority to vector-only is claimed.
- **Trust:** source text is SOURCE_LOCATED; generated interpretations are HYPOTHESIS.
  Exact quotes/IDs are mechanically checked, but semantic entailment still needs review.
  Graph paths require SOURCE_VERIFIED plus explicit student approval metadata and
  valid source support. No automatic CITES creation, research import or alias merge.
- **Security:** only fixed parameterized read templates, no raw Cypher capability.
  READ routing is not database-level authorization in Community. Bolt stays internal;
  write CLI remains outside the tool registry. Unknown tools/fields, invalid IDs,
  source mismatches, malformed model output and unbounded parameters are rejected.
  Cloud tracing is disabled. Gold is read only by an offline smoke driver, which sends
  question strings alone to the API; it is absent from the service image and context.
- **Alternatives/drawbacks:** a fixed RAG chain lacks the requested model-selected
  loop; unrestricted generated Cypher is unnecessary risk; hosted APIs violate budget.
  CPU tool calling may abstain or hit budgets. ANN post-filtering is approximate and
  can miss paper-restricted hits beyond the bounded candidate set. Generalization and
  semantic answer quality require separate evaluation, not schema checks alone.
- **Status:** implementation authorized by prompt #6; actual tests and live outcomes
  are recorded in [AGENT.md](AGENT.md), rather than inferred from this decision.
  Remaining student gate: approve actual citation/scientific claims before verified
  graph demonstrations. No human approval is supplied by this milestone.

## D17 — PROVISIONAL Chunk-classification decision, 2026-10-20

- **Authority:** prompt #5.2 explicitly requests a provisional switch from citation
  prediction to Method-versus-Evaluation classification of existing Chunk nodes.
  No training, automatic approvals, alias merges or additional ingestion is authorized.
- **Decision:** adopt that task provisionally, conditional on source-reviewed chunk
  labels, eight real label-blind graph-neighborhood features and a held-out whole-paper
  test split. D06's citation-link proposal is historical and superseded for ML planning.
- **Rationale:** 0 approved CITES edges in the live prototype and 13 research-located
  references across ten papers do not provide an audited citation label matrix or
  meet the proposed 50-positive gate. Prose roles are more practical to annotate.
- **Proposed protocol:** train on v1 DPR/RAG/REALM/FiD/Self-RAG/LightRAG and hold out
  v1 GraphRAG/HippoRAG. Targets of 96 labels and 8 papers are not achieved statistics.
  Independently review test labels; freeze split/settings before fitting. Derive
  counts/overlaps/existence flags solely from within-paper MENTIONS/NEXT neighborhoods.
  Training-only preprocessing; majority baseline versus one regularized logistic model;
  macro-F1, per-class and per-paper results. See ARCHITECTURE.md section 7 for gates.
- **Alternatives:** citation prediction remains possible future work after a complete
  reference audit; text/section heuristics or LLM class guesses are not this graph ML
  workflow. GDS analytics remain a separate requirement.
- **Drawbacks/gates:** sparse and noisy entity extraction may make all features constant;
  only three papers are currently ingested; no reviewed ML labels exist. Two test papers
  and purposive balanced sampling limit generalization. Report blocked/incomplete if
  features, reviews or a proper split cannot be produced; do not train on gold QA labels.
- **Status:** PROVISIONAL, not implemented or evaluated. Unapproved research candidates
  remain pending; student identity resolution, labels and semantic approvals are still
  required. The gold file's assistant SOURCE_VERIFIED status is not graph approval.

## D16 — PR #2 ingestion integrity corrections, 2026-10-20

- **Authority:** prompt #5.3 requests entity/chunk integrity, required citation failure
  handling and atomic PDF publication; no corpus expansion or new features.
- **Decision:** validate entity references before opening the paper write transaction.
  Preflight all required in-corpus citations before any graph writes. On failure,
  mark the affected paper FAILED and other papers NOT_STARTED; retain evidence ID,
  paper ID and failure reason, report a core failure and exit 1.
- **Alternative/tradeoff:** skipping only an affected paper could leave unresolved
  cross-paper targets or newly registered metadata for a failed source. A whole-run
  preflight is simpler and prevents those partial writes, at the cost of deferring
  otherwise valid imports until the citation input is corrected. Existing graph
  evidence is untouched. Optional LLM failures keep their existing partial-success contract.
- **Files:** use a temporary file in the destination directory, flush/fsync, verify
  its complete bytes/hash, then atomically replace the destination. Exceptions remove
  temporary files and preserve an existing valid PDF; verified downloads are still reused.
- **Status:** implemented and tested; no additional student decision is required for
  these explicitly requested fixes. See INGESTION.md for actual verification results.

## D13 — Local infrastructure authorization, 2026-10-19

- **Decision and authority:** the user explicitly authorized local downloads, builds, container startup and smoke tests for this milestone. Deadline is **Friday, October 23, 2026** (Europe/Paris); team size is **two students**, with the user as team lead. Budget is **strictly zero** paid APIs, cloud services or subscriptions. Hosted paid fallback is excluded. Do not commit, push, publish images or ingest papers during this task.
- **Observed hardware:** Windows/WSL2 Ubuntu; Intel Core Ultra 9 285H; 16 logical processors; WSL 15.30 GiB RAM and 4 GiB swap; Windows reports 31.36 GiB physical RAM. Docker Desktop exposes the same 15.30 GiB ceiling. Intel Arc 140T and `/dev/dxg` were observed; usable Ollama acceleration is unverified. Use CPU inference only. WSL reported about 951 GiB virtual filesystem space, while Windows C: had about 719 GiB free during the audit.
- **Provisional architecture approved for this milestone:** Neo4j Community 5.26.32 + GDS 2.13.2, Python 3.12 API, and Ollama 0.40.6 in three Compose services. Pin the official GDS JAR SHA-256. Container RAM caps: Neo4j 4 GiB, Ollama 6 GiB, API 1 GiB (11 GiB total); no additional container swap; CPU quotas 3/8/2. Only API port 8000 is published, bound to localhost. All database/model traffic stays on the Compose network.
- **Models selected for a trial:** `qwen2.5:3b-instruct`, Q4_K_M, about 1.9 GB; `nomic-embed-text:v1.5`, about 274 MB. Actual installed digests/sizes and model behavior must be recorded after download. Limit one loaded model and one inference request, 2048-token default context; model switching may add latency.
- **Licenses and sources checked before downloading:** [Qwen 3B's Research License](https://ollama.com/library/qwen2.5:3b-instruct/blobs/b5c0e5cf74cf) permits non-commercial research/evaluation and is not Apache 2.0. [Nomic v1.5](https://huggingface.co/nomic-ai/nomic-embed-text-v1.5) is Apache 2.0. [GDS 2.13.2 release notes](https://github.com/neo4j/graph-data-science/releases/tag/2.13.2) explicitly fix Neo4j 5.26 Community compatibility; [GDS source license](https://github.com/neo4j/graph-data-science/blob/2.13/LICENSE.txt) is GPLv3, with separate commercial Enterprise features not required here. Neo4j uses the Community image; no Enterprise subscription/license key is configured. Respect upstream notices; weights are stored only in a local named volume.
- **Alternatives:** hosted LLM + Nginx remains historical planning context and is not selected; paid usage is prohibited. GPU troubleshooting and alternative models are deferred unless smoke evidence identifies a focused zero-cost remedy.
- **Rationale:** establish a reproducible foundation within the measured WSL ceiling and short deadline without spending time on unverified Intel acceleration.
- **Drawbacks:** CPU latency and small-model tool reliability remain unknown until tested; a successful small tool-selection request will not establish a functioning LangGraph agent.
- **Status:** IMPLEMENTED AND SMOKE-VERIFIED for the infrastructure scope on 2026-10-19; see [actual results](INFRASTRUCTURE.md). All three services healthy; exact Neo4j/GDS versions checked; GDS runs without an Enterprise key; four real CPU model cases passed; 12 health/connectivity tests passed. This does not approve later application behavior or claim full rubric completion. D01–D06 and D09–D11 application-level choices remain proposed. Initial CI/lint, application schema, GDS analytics and ML are not included in this milestone.
- **Questions:** exact student names/task distribution and remaining project approvals are still needed; no further approval is required to execute the downloads/builds/smoke tests already authorized by this prompt.

### D13 verification notes and provisional model acceptance

The selected Qwen/Nomic models passed basic text, schema-constrained JSON, one actual tool-selection/argument case and embedding generation on CPU. Qwen's first response took 5.012 s including model load; subsequent JSON/tool requests took 1.054/2.613 s; Nomic embedding took 0.591 s. Accept these as initial local candidates for later evaluation, not as validated research-paper extractors or a functioning agent. Model digests and exact byte sizes are in `../models.lock.json`.

Observed kernel memory peaks since container creation were Neo4j 2.073 GiB, Ollama 4.104 GiB and API 0.142 GiB, below their 4/6/1 GiB caps; no container OOM events. Keep the current CPU-only, one-request/one-resident-model limits until realistic workloads are measured. Host Make remains absent, but a locally extracted GNU Make ran the targets; normal student setup needs Make installed/on PATH.

GDS source/binary license distinction: the official JAR includes an Enterprise/pre-release `LICENSE.txt`; do not describe the entire binary as GPL solely from the OpenGDS source license. Official edition documentation states Community is the default; `gds.isLicensed()` returned false and the Community procedures executed. No paid feature/key or subscription was used. Preserve notices and clarify binary redistribution terms before any future custom Neo4j image publication; this task published nothing.

## D15 — Bounded ingestion corrections, 2026-10-20

- **Authority:** prompt #5.1 supersedes D14's automatic SOURCE_VERIFIED exception.
  The deadline, zero-cost restriction, corpus, branch and infrastructure are unchanged.
- **Decision:** source location and semantic review are separate. Bibliography checks
  yield EXTRACTED claims with SOURCE_LOCATED, location policy and time. SOURCE_VERIFIED
  requires a named student's explicit approval, note and timestamp under
  `student-semantic-review-v1`. The local review method records an attestation; it
  cannot authenticate the operator's identity and is never invoked by the extractor.
- **Existing evidence:** migrate only legacy automatically approved bibliography
  claims back to pending review, retaining prior properties in append-only JSON review
  history. Keep claim IDs, quotations, pages and support relationships. Remove derived
  CITES until human approval; status alone cannot recreate an edge.
- **Extraction:** the saved DPR output paired Method with ADDRESSES and its quote did
  not include the named entity; GraphRAG silently changed `in- dexed` to `indexed`.
  Both failures remain rejected. Do not guess dehyphenation or repair predicates.
  Select bounded explicit-use prose from the unchanged PDFs. For method samples,
  embed one Method entity inside its USES relation, eliminating duplicated names;
  retain strict quote membership, offsets, type checks and EXTRACTED status.
- **Alternatives/drawbacks:** fuzzy matching or automatic predicate rewriting would
  obscure evidence errors. Manual semantic review remains necessary; curated method
  passages are development smoke samples, not unbiased extraction evaluation.
- **Exit contract:** default exit 0 means core import succeeded, even if optional
  extraction failed (PARTIAL_SUCCESS). Core failures exit 1. `--require-extraction`
  requests exit 2 for optional extraction failure. Reports keep per-paper import,
  overall, extraction and failure details; failed caches are retained.
- **Status:** implemented; actual tests, timings and graph counts are recorded in
  INGESTION.md. No real student approvals are asserted or applied in this task.
- **Next approval:** students must inspect citation context/identity and semantic
  claims before explicitly approving any SOURCE_VERIFIED transitions.

## D14 — Three-paper evidence ingestion authorization, 2026-10-20 (historical; policy superseded by D15)

- **Authority/scope:** prompt #5 explicitly authorizes ingestion on `feat/document-ingestion`
  of DPR `2004.04906v1`, RAG `2005.11401v1`, and GraphRAG `2404.16130v1`
  from the supplied manifest. Existing corpus research files and professor documents
  are immutable inputs. Deadline and zero-cost restriction remain unchanged.
- **Decision:** pin pypdf 6.10.0 to reproduce the research page hashes; normalize
  per-character NFKC and whitespace with reversible character-span mappings. Use
  page-bounded 1400-character windows with approximately 200-character overlap and
  whitespace boundaries. These are character limits, not claimed token counts.
  Preserve raw pages, mappings, parser warnings and all extraction attempts locally.
- **Graph:** implement Paper, Chunk, Entity, optional Topic and Claim, four uniqueness
  constraints and lookup indexes. Only independently validated citation claims supply
  derived CITES. Scientific entity candidates remain paper-scoped until reviewed
  aliases justify cross-paper resolution.
- **Citation policy approval:** the team lead explicitly answered **“Allow automated
  bibliography verification”** during this task. This supersedes the student-only
  SOURCE_VERIFIED rule **for bibliography identity only**. Policy
  `automated-bibliography-v1` checks pinned PDF/page hashes, title coordinates,
  normalized target title, reference-section/entry context, first author, and work
  identity (explicit arXiv ID when present). Record automated reviewer/policy/time,
  while `student_review_status=pending`. It does not claim a human reviewed the
  source or that the citing author read the selected target v1.
- **Extraction:** one first-page sample per paper by default; maximum two; strict
  structured output, exact entity/quote matching, fixed predicates/ranges, digest-pinned
  local Qwen, one request at a time. Automatic scientific claims stay EXTRACTED.
  Failures are saved and reported, not silently retried or promoted.
- **Re-import:** deterministic identities, UNWIND batches and one transaction per
  paper. Reuse raw extraction cache and revalidate successful output. Preserve
  existing claim review status; rebuild only the source paper's derived citations.
  A PDF/parser/chunker change for an existing version requires an explicit migration.
- **Alternatives:** larger token/paragraph chunks; layout-aware/OCR parsing; globally
  merging names; a web import endpoint. These add unresolved parsing/resolution or
  authentication scope. A local CLI is the smallest authorized entry point here.
- **Drawbacks:** text order and semantics still need student inspection; conservative
  entity resolution limits cross-paper concept joins; a tiny extraction sample does
  not measure corpus-wide precision/recall. Automated bibliography checks are narrower
  than semantic human review.
- **Status:** IMPLEMENTED; actual execution evidence and limitations are recorded in
  [INGESTION.md](INGESTION.md). No agent, vector ingestion, analytics or ML is authorized
  by this milestone.
- **Remaining student decisions:** review semantic claims and PDF quality; approve
  aliases before global concept merging; scope the first retrieval/agent slice.

## D01 — Corpus selection and size (original proposal)

- **Decision:** use an AI retrieval/GraphRAG paper corpus, growing from 3 prototype papers to approximately 10 development papers and 20–30 evaluated papers if practical. The three candidates and sources are in [PROJECT_BRIEF.md](../PROJECT_BRIEF.md).
- **Alternatives considered:** a broad AI corpus; technical documentation; arbitrary web documents; immediately ingesting hundreds of papers.
- **Rationale:** a focused topic makes cross-paper relations and manual verification manageable while keeping Project 8's scientific-document specialization.
- **Drawbacks:** selection bias, limited diversity, PDF parsing problems and too few verified citation links for ML. Public accessibility does not settle redistribution rights.
- **Status:** PROPOSED.
- **Questions requiring student approval:** approve the topic and three candidates? What review time and corpus-size ceiling are acceptable? May the corpus expand if citation labels are insufficient? Who approves PDF versions and license notes?

## D02 — Evidence-first graph schema

- **Decision:** Paper, Chunk, Entity and Claim nodes, with Topic as an additional Entity label; directed evidence/subject/object relationships; only verified citations get derived `CITES` edges. Method/Dataset/Task are Entity kinds. Authors remain Paper metadata.
- **Alternatives considered:** direct extracted edges only; generic `RELATED_TO`; a large ontology with separate author, venue, page, experiment and result nodes; names stored only in string arrays.
- **Rationale:** claims preserve per-source quotations, review state, qualifications and conflicting assertions. Shared entities support graph joins; derived citations simplify shortest paths without discarding evidence.
- **Drawbacks:** more hops, validation code and review work; derived citations must be rebuilt when source review changes. Entity resolution can still introduce errors.
- **Status:** PROPOSED.
- **Questions requiring student approval:** are the four initial predicates sufficient for the intended questions? Is human source verification before factual graph expansion feasible? Is the added Claim-node complexity defensible by every team member?

## D03 — PDF parsing and LLM extraction

- **Decision:** start with pypdf page extraction, page-bounded paragraph chunks, structured LLM claims and explicit quote/offset validation. Preserve parsing, prompt and model versions; review aliases and relation meaning manually.
- **Alternatives considered:** layout-aware PDF parser; OCR; rules-only extraction; end-to-end opaque document-to-graph library.
- **Rationale:** exposes the pipeline clearly for academic explanation and keeps page citations auditable. Structured extraction handles varying scientific wording while validation catches unsupported outputs.
- **Drawbacks:** multi-column layouts, tables and equations may fail; exact quotation matches do not prove semantic entailment; manual review and extraction consume time.
- **Status:** PROPOSED.
- **Questions requiring student approval:** accept text-only PDFs and deferral of table/equation interpretation? Approve the initial 500-token/75-token overlap targets and sample-review gate? If parsing fails, which alternative and additional scope are affordable?

## D04 — Vector store and hybrid retrieval

- **Decision:** keep chunk embeddings in Neo4j, retrieve vector seeds, expand via bounded verified-claim traversal and fuse candidate ranks. Keep a vector-only evaluation baseline.
- **Alternatives considered:** separate Qdrant/FAISS service; lexical-only search; graph-only retrieval; a learned reranker.
- **Rationale:** one storage system reduces operational work and lets retrieval retain graph/evidence identifiers directly. The comparison tests whether graph expansion actually helps.
- **Drawbacks:** vector behavior depends on Neo4j/model versions; rank fusion needs tuning; graph expansion may add irrelevant context. Replacing the embedding model requires rebuilding embeddings and the index.
- **Status:** PROPOSED.
- **Questions requiring student approval:** approve native Neo4j vectors and the bounded hybrid method? Which embedding model/license and memory budget are acceptable? What context budget should be frozen for fair evaluation?

## D05 — GDS projection and algorithms

- **Decision:** project papers connected by shared entities from source-verified claims, with undirected Jaccard weights; run weighted PageRank and Louvain. Keep all papers, including isolates.
- **Alternatives considered:** citation-only projection; full heterogeneous graph; degree plus connected components; embeddings-based similarity edges.
- **Rationale:** paper similarity is an understandable navigation task and avoids allowing chunk count or unreviewed relations to drive metrics. PageRank provides ranking; Louvain provides grouping. Both are genuine GDS computations.
- **Drawbacks:** weighted PageRank can resemble degree on this graph; Louvain may be unstable or uninformative for a tiny corpus; broad entities can dominate connections. The projection is a derived similarity model, not scientific influence.
- **Status:** PROPOSED.
- **Questions requiring student approval:** are ranking and grouping useful demo questions? Approve this projection and weight definition? What would justify a projection change if all papers form a near-clique or remain isolated?

## D06 — Graph-based ML (historical proposal; superseded provisionally by D17)

- **Decision:** evaluate held-out citation-link reconstruction using logistic regression on training-graph topology and GDS PageRank features. Compare against prevalence and preferential-attachment baselines; treat predictions as hypotheses.
- **Alternatives considered:** GDS-native link-prediction pipeline; paper/topic node classification; GNN training; calling an unsupervised similarity score “ML.”
- **Rationale:** a small supervised model makes leakage controls, features and errors explainable. A score alone does not demonstrate a trained ML workflow. Using scikit-learn keeps the training process visible while features remain graph-based.
- **Drawbacks:** 20–30 papers may be inadequate; citation absence must be checked against readable references; a transductive random-edge experiment does not demonstrate future-paper generalization. Small samples make metrics noisy.
- **Status:** PROPOSED.
- **Questions requiring student approval:** approve the citation task and provisional 50-positive-link feasibility gate? If the gate fails, approve expansion or a different reviewed-label task before changing scope. Confirm with the professor whether an external learner with GDS features is acceptable if a GDS-native training pipeline is expected.

## D07 — LLM provider and resource budget

- **Decision:** prefer local Ollama for structured extraction, generation and tool calling, with a separately chosen embedding model. Select and pin models only after hardware and structured-output smoke tests.
- **Alternatives considered:** hosted model API; separate local runtimes; multiple providers with automatic fallback.
- **Rationale:** local inference can avoid paid API requirements and supplies a meaningful third Compose service. A single provider limits integration work.
- **Drawbacks:** model memory and latency may exceed laptop capacity; smaller models may struggle with extraction and tool arguments; image availability does not prove model licensing suitability. Downloading models is a separate setup step.
- **Status:** PROPOSED.
- **Questions requiring student approval:** what CPU/GPU/RAM is available and what latency is acceptable? Is a hosted provider and spending cap permissible if local results fail? Which model/license may be used? No paid service or model has been selected.

## D08 — Three Docker services

- **Decision:** Neo4j+GDS, FastAPI and Ollama under Compose; scripts reuse the application image/modules. Use named persistence volumes and localhost access for the demo. Publish the custom API image to a public registry later.
- **Alternatives considered:** hosted inference plus Nginx as the third service; a separate vector store; asynchronous worker/queue; an unused container added just to reach three services.
- **Rationale:** each proposed service has a distinct functional role, and no queue or extra database is needed for bounded imports. Authentication on import covers the rubric's security option.
- **Drawbacks:** inference competes for local resources; a synchronous import needs tight limits; model provisioning complicates first startup. A hosted-provider change requires a reviewed service redesign.
- **Status:** PROPOSED.
- **Questions requiring student approval:** approve the three-service arrangement and local deployment scope? Which public registry/account and image name will be used? Who can authorize actual publication? Which machine must reproduce the stack?

## D09 — One constrained LangGraph agent

- **Decision:** one stateful tool-calling LangGraph agent with conditional loops, explicit budgets, evidence accumulation and validated structured answers. Expose tool events and graph paths. The LLM selects reviewed query templates and typed parameters.
- **Alternatives considered:** one prompt with concatenated passages; a fixed retrieval chain; multi-agent delegation; free-form NL-to-Cypher with a keyword blocklist.
- **Rationale:** demonstrates genuine Level 3+ behavior while keeping execution inspectable. Template selection still allows multi-step decisions and avoids executing arbitrary generated query text.
- **Drawbacks:** a finite tool set cannot answer every possible graph question; model tool-calling quality needs evaluation; state and error handling add complexity beyond a single prompt.
- **Status:** PROPOSED.
- **Questions requiring student approval:** approve the tool set, six-call initial budget and abstention policy? Confirm the intended research questions fit the available templates. No raw-Cypher capability is proposed.

## D10 — Evaluation and scientific honesty

- **Decision:** frozen corpus/version manifests, manually annotated evidence, a held-out question set, vector-only versus hybrid comparison, leakage-controlled ML splits, separate graph/LLM latency measurements and explicit failure reporting.
- **Alternatives considered:** anecdotal demos only; LLM-as-judge alone; generated labels treated as truth; evaluating on development prompts; claiming improvement from a larger context budget.
- **Rationale:** the project must demonstrate reliability and explain limitations. Controlled comparisons isolate graph retrieval's contribution.
- **Drawbacks:** annotations are costly, questions can be biased, and small corpora limit conclusions. Some live model runs will not be perfectly reproducible.
- **Status:** PROPOSED.
- **Questions requiring student approval:** approve the proposed 100-claim and 30-question evaluation targets and thresholds in ARCHITECTURE.md? Who independently reviews a subset? How much time is reserved for evaluation rather than extra features?

## D11 — Authentication and query isolation

- **Decision:** authenticate import with an environment-provided secret, isolate ingestion from agent tools, and execute only reviewed read templates or named GDS streaming tools with budgets. Use database read-only privileges where the selected edition supports them.
- **Alternatives considered:** Nginx-only security; full user management/OAuth; trusting driver read routing; exposing Neo4j directly to an LLM.
- **Rationale:** one protected sensitive endpoint satisfies the rubric's authentication option without a user-management subsystem. Tool capabilities and parameters are narrow enough to test.
- **Drawbacks:** a local shared secret is not production authorization; Community-edition permissions may limit database-level separation. Application checks must not be described as a database-enforced role.
- **Status:** PROPOSED.
- **Questions requiring student approval:** approve local-only deployment and shared-secret import? Is a stronger database security edition available/required? Any public deployment would need a separate security decision.

## D12 — Compatible versions and reproducible delivery

- **Decision:** honor Neo4j 5.x; use 5.26/GDS 2.13 as a candidate family from the official matrix, then pin tested patches/digests, Python packages and models. Create early GitHub Actions checks and graduate to full integration/health checks before release.
- **Alternatives considered:** unpinned latest images/plugins; upgrading the professor's stack to a new major generation; postponing integration until the demonstration.
- **Rationale:** [Neo4j's compatibility matrix](https://neo4j.com/docs/graph-data-science/current/installation/supported-neo4j-versions/) explicitly pairs release families. A tested manifest and CI evidence make failures reproducible.
- **Drawbacks:** exact availability/support/licensing and procedure behavior still need checking; older specified families may require careful patch selection. A pinned dependency can still have defects.
- **Status:** PROPOSED.
- **Questions requiring student approval:** approve this release-family investigation? If no acceptable supported pair meets course constraints, who will request professor clarification? Who maintains version pins and release evidence?

## Open planning inputs

The user confirmed the team lead (user), two-student team, Friday October 23 deadline, observed hardware and strict zero-cost budget in D13. Individual names/task assignments, annotation capacity, registry destination and application-level approvals remain open. The professor's externally linked pylint configuration was not accessible through the planning lookup; inspect it before implementing lint configuration. These remaining uncertainties do not block the explicitly authorized infrastructure work. No broader application approval is inferred from the existence of these documents.
