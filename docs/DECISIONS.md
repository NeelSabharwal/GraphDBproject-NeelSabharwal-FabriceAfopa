# Proposed decision register

The D01–D12 entries preserve the original **PROPOSED** design. D13 supersedes conflicting budget, scheduling and runtime assumptions; D14 records the subsequent ingestion authorization and explicit bibliography-policy approval. The professor's [specification](requirements/projects_spec.md) and [checklist](requirements/project_checklist.md) remain authoritative. Record approval/rejection, date, participants and supporting evidence when a decision is resolved; update [ARCHITECTURE.md](ARCHITECTURE.md) and [PROJECT_PLAN.md](../PROJECT_PLAN.md) together.

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

## D06 — Graph-based ML

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
