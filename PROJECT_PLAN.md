# Project plan — AI Research GraphRAG Assistant

**Status: application milestones remain PROPOSED; local infrastructure is now explicitly authorized.** The [professor's specification](docs/requirements/projects_spec.md) and [100-point checklist](docs/requirements/project_checklist.md) are authoritative. No grading credit is claimed without evidence.

## Infrastructure scope update — 2026-10-19

The user authorized a narrow foundation milestone ahead of the original M01 dependency: three local Docker services, Python 3.12 health-only FastAPI, pinned Neo4j/GDS, CPU Ollama model trials, starter Make commands and meaningful health/connectivity tests. This authorizes only part of M02, not its future CI/lint items or later application milestones. Deadline is **Friday, October 23, 2026**, team size **two**, user is team lead, and paid APIs/cloud/subscriptions are prohibited. See decision D13 and the eventual actual verification report. The rubric table below remains a planning map; existence of health endpoints does not satisfy the advanced API requirement. No commit, push, public image publication or ingestion is authorized here.

**Actual foundation evidence:** [INFRASTRUCTURE.md](docs/INFRASTRUCTURE.md) records three healthy containers, exact versions, four passing real CPU model checks, and a full **12 passed** health/connectivity suite with **100% coverage of 72 current statements**. This verifies only the implemented foundation. M02 remains partial because CI/lint and later schema/vector readiness are outside this task. The original checklist mapping/statuses below are retained as the planning baseline; consult the dated evidence rather than treating all points as earned. Host Make installation/PATH setup and GDS binary redistribution clarification remain documented limitations.

### Ingestion scope update — 2026-10-20

Prompt #5 authorizes the prototype part of M01/M03 on `feat/document-ingestion`.
The three supplied manifest versions, provenance graph, bounded extraction,
bibliography verification, repeatable local CLI and tests are now implemented.
The team lead separately approved automated bibliography verification (D14).
[INGESTION.md](docs/INGESTION.md) records actual results, failures and limitations.
The import HTTP endpoint/authentication, development-corpus expansion, alias review
and later retrieval/agent work remain incomplete. The exact rubric mapping below
is preserved; this milestone does not by itself complete M03 or the grading checklist.

## Observed starting point (historical planning baseline)

Repository inspection on 2026-10-19 found `main` tracking `origin/main`, a tracked one-line README, an existing untracked `.gitignore`, four empty planning placeholders, both professor documents, and the requested empty application/data/script/test folders. `.git/`, `.agents/`, `.aws/` and `.codex/` were also present. No application, Docker setup, tests, CI workflows or implementation evidence was found. Git status already included untracked planning and requirements files before this task. Remote reviews, branch activity and contributions have not been audited.

The five planning documents are the output of this task. README, `.gitignore`, professor documents and unrelated content are preserved. No code, Docker configuration, dependency installation, ingestion, commit or push is part of this planning task.

## Milestones, dependencies and acceptance criteria

Each milestone starts after its listed dependency is accepted. Keep PRs small: a milestone may require several PRs, each with its own test evidence. Owners/reviewers are to be assigned by the student team lead. Dates depend on the still-unconfirmed deadline and available effort. CI, tests and documentation begin with the first relevant implementation rather than being deferred to the final milestones.

| ID / proposed branch | Dependency | Scoped deliverables | Acceptance criteria and evidence |
| --- | --- | --- | --- |
| M00 — Scope and coordination; `docs/approve-scope` | This planning draft reviewed | Student-approved decision entries, team lead/member roster, hardware/budget/deadline, task and reviewer assignments, contribution plan | Resolve D01–D12 as needed for the next milestone; record outstanding gates. Plan at least one substantial merged PR per member and meaningful work distribution. No implementation starts merely because a proposal exists. |
| M01 — Corpus and schema; `feat/corpus-schema` | M00 | Prototype manifest targeting 3 papers, parser sample inspection, reviewed schema/constraint/index design, baseline AI schema artifact, editable graph diagram | Verify candidate versions/access/license notes and page quality. Demonstrate intended questions through manually checked paths. Explain chosen model versus the saved generic schema; students revise and defend it. No dataset statistics are claimed until measured. |
| M02 — Reproducible runtime; `chore/runtime-ci` | M01 | Python environment/dependencies, Compose with 3 justified services, custom API Dockerfile, pinned Neo4j/GDS, `.env.example`, health endpoints, initial Makefile/CI, `.pylintrc` after reviewing linked rules | Clean startup on the target machine; real database query, model smoke inference, GDS/version and vector-index checks. Lint and first meaningful tests run in GitHub Actions. Required Make targets have real behavior as modules become available; record any incomplete targets. |
| M03 — Evidence ingestion; `feat/evidence-ingestion` | M02 | PDF parsing/chunking, constrained extraction, review records/aliases, schema migrations, authenticated import endpoint and resumable CLI script, provenance fixtures | Import prototype twice without duplicates; reject malformed/unsupported claims; preserve pages/quotes/statuses. Test constraints and authentication. Grow toward approximately 10 development papers only after quality review; inspect preliminary citation-label feasibility early. |
| M04 — Early LangGraph slice; `feat/agent-retrieval` | M03 | Embeddings/index, vector-only baseline, hybrid retrieval tools, typed state/conditional loop, structured response and trace, `/api/ask` | Real question uses multiple tools and cites actual chunks/paths. Invalid model output or unsafe template request is rejected. Test budgets, ambiguity and abstention. Save actual tool trace and distinguish mocked tests from live-model evidence. |
| M05 — Advanced graph API; `feat/graph-queries` | M04 | Topic evidence traversal, directed citation shortest-path endpoint, Pydantic models/errors, parameterized query registry, Cypher fixtures | Complex patterns and analytical `WITH`/`UNWIND`/subqueries/aggregation produce expected fixture results. Test path direction, hop limits, pagination, no-path and missing IDs; retain query plans. Endpoint count is not yet final until GDS routes in M06. |
| M06 — GDS analytics; `feat/gds-analytics` | M05 | Versioned paper-similarity projection, PageRank and Louvain, centrality/community endpoints, projection lifecycle/explanation mapping | Verify nodes/weights/isolates and memory estimate; run both algorithms on fixture and corpus. Demonstrate actual GDS call from endpoint and pathfinding from M05. At least 4 domain endpoints, 3 advanced queries and 2 pathfinding/algorithm endpoints are now verifiable. |
| M07 — ML experiment; `feat/link-prediction` | M06 | Approved evaluated-corpus target of 20–30 papers if practical, reviewed citation labels, split files, graph/GDS features, logistic-regression workflow, baselines and metric report | Pass label feasibility gate or record blocker and seek revised scope. Remove held-out edges before feature construction; verify no label leakage. Record actual counts, PR-AUC/other metrics, baselines, seeds and limitations. Predictions remain hypotheses; weak results may be reported honestly. |
| M08 — Evaluation and performance; `test/evaluation-benchmarks` | M07, or explicit revised scope if ML is blocked | Frozen question/annotation sets, vector-only/hybrid comparison, extraction and guardrail evaluation, before/after query benchmarks, `EXPLAIN`/`PROFILE` artifacts | Apply predeclared targets in ARCHITECTURE.md; report all successes/failures and actual latency. Test independent questions, equal retrieval budgets and source support. Inspect index usage, avoid Cartesian products, and document limits. An ML blocker remains visible even if independent evaluation proceeds. |
| M09 — Quality and automation gate; `test/release-quality` | M08 | Complete unit/API/Neo4j/Cypher/health suites, full Makefile, lint/test/build workflows, coverage reports and badge wiring, clean code/docstrings | Run full `make test` including Cypher and required integration checks; all required tests pass with coverage ≥60%. `make lint` scores ≥9.5. Confirm fresh Compose startup and health failure handling. Exercise all required Make commands in a disposable workspace, including safe clean behavior. |
| M10 — Documentation and registry; `docs/release-evidence` | M09 | Complete README, actual screenshots and diagrams, executed `demo.ipynb`, anti-genericity appendix, contribution/PR links, published API image and digest | A teammate follows README from fresh checkout, pulls public image and runs the stack. Registry link resolves. Notebook executes with actual graph visualizations. README badges reference real workflows/reports. Publication occurs only when separately authorized. |
| M11 — Live defense and final audit; `docs/demo-audit` | M10 | Live-demo runbook, evidence index mapping each checklist row to actual artifacts, contribution audit, final limitations and approved decisions | Run `make help`, `make lint`, `make test`, `make docker-run`; show Neo4j/API/Swagger, images, GDS/ML, contribution history and merged PRs. Show successful agent request and rejection of invalid LLM output. Students explain model/index/algorithm/guardrail decisions. Missing evidence remains unverified. |

M07's feasibility gate may block ML acceptance; it must not be bypassed by claiming that a proposed experiment meets the rubric. Independent work may continue only within an explicitly agreed revised sequence. Corpus growth is a target, not a substitute for good extraction, meaningful graph analysis or evaluated labels.

## Collaboration and evidence workflow

- Keep `main` stable. After authorization to implement, use at least two active branches, with feature branches used by team members. The branch names above are proposals, not existing branches.
- Assign authors and another student reviewer before each task; rebalance substantial code, tests, analysis and documentation as work proceeds. Do not inflate contribution counts with cosmetic commits.
- Require at least two constructive review comments per PR, with responses or follow-up changes, and retain PR URLs/screenshots. Each member needs at least one substantial merged PR. A planning PR alone must not be assumed substantial enough.
- Use clear messages such as `feat:`, `fix:`, `test:`, `docs:`, `refactor:` and `chore:`. Record actual merge/review evidence; do not invent history.
- Run lint on push/PR and tests with coverage in GitHub Actions. Add an image-build workflow and actual build/test/coverage badges. Heavy real-model evaluation can run separately, but mocked CI does not establish that the live model works.
- At M11 inspect `git shortlog -sn`, GitHub Contributors and per-member PRs. Assess substance as well as counts. Record contributor names and percentages from actual evidence, never from the professor's example table.

## Rubric mapping and status definitions

The following table copies all **49** criteria and point allocations from the standalone checklist. Detailed acceptance requirements from the full specification are included in the deliverable/verification columns and milestones. **PLANNED** means future work has been assigned; **NOT VERIFIED** means an artifact or relevant prior state exists but has not been validated against the criterion. Neither status means satisfied or points earned. No criterion is marked complete.

The existing `.gitignore` is NOT VERIFIED: its presence and text were observed, but there has been no complete tracked-history/secret/ignore-behavior audit. Other rows remain PLANNED even where these documents contain preliminary design material.

| ID | Professor category | Exact checklist criterion | Points | Milestone(s) | Expected deliverable | Verification method | Current status |
| --- | --- | --- | ---: | --- | --- | --- | --- |
| R01 | **Docker Infra & Services** | `docker-compose.yml` with ≥3 services | 2 | M02, M09 | Compose with Neo4j/GDS, API and Ollama | Validate Compose configuration; clean startup and inspect three functional services | PLANNED |
| R02 | **Docker Infra & Services** | Proper `Dockerfile` / official image | 2 | M02, M10 | API Dockerfile; pinned official images and GDS packaging record | Build custom image; inspect official-image configuration and plugin version; run built image | PLANNED |
| R03 | **Docker Infra & Services** | `.env.example`, no secrets committed | 2 | M02, M09 | .env.example and environment configuration; no hardcoded secrets | Review configuration, image build context and tracked history; test required-variable handling without printing secrets | PLANNED |
| R04 | **Docker Infra & Services** | ≥1 image on public registry | 2 | M10 | Public API image URL and immutable digest in README | After authorized publication, anonymously pull and run the published image; retain registry evidence | PLANNED |
| R05 | **Docker Infra & Services** | Docker Compose starts cleanly | 1 | M02, M09, M11 | Reproducible Compose startup and setup instructions | Start on a fresh documented environment; check logs, readiness and actual endpoint responses | PLANNED |
| R06 | **Neo4j Database** | Schema: ≥3 labels, ≥3 relation types | 3 | M01, M03 | Paper/Chunk/Entity/Claim schema, typed relationships and meaningful properties | Inspect loaded database labels/types/properties and demonstrate domain queries; diagram alone is insufficient | PLANNED |
| R07 | **Neo4j Database** | ≥2 constraints | 2 | M03 | At least Paper.id and Chunk.id uniqueness constraints, plus Entity/Claim identities | Inspect SHOW CONSTRAINTS and test duplicate rejection | PLANNED |
| R08 | **Neo4j Database** | Appropriate indexes | 2 | M03, M08 | Identity, entity-lookup and chunk-vector indexes justified by workload | Inspect SHOW INDEXES, index readiness and actual query plans/latency | PLANNED |
| R09 | **Neo4j Database** | Dataset ingestion script | 2 | M03 | Selected-PDF ingestion script with provenance, validation and resumability | Run against approved manifest; repeat import and test idempotency/failure recovery | PLANNED |
| R10 | **Neo4j Database** | Dataset source documented | 1 | M01, M10 | Versioned source manifest and README dataset rationale | Resolve source identities, inspect version/license notes and PDF hashes; check justification against intended questions | PLANNED |
| R11 | **FastAPI** | ≥4 endpoints, ≥3 advanced graph queries | 2 | M05, M06 | Domain endpoints including topic traversal, citation paths and GDS centrality | Run API tests and live calls: at least 4 endpoints, at least 3 actual advanced queries | PLANNED |
| R12 | **FastAPI** | Pydantic validation | 2 | M03–M06 | Pydantic input/output models including evidence and bounded query parameters | Test malformed requests, invalid IDs/enums/limits and response-schema enforcement | PLANNED |
| R13 | **FastAPI** | Swagger `/docs` works | 1 | M02, M09, M11 | Working OpenAPI schema and Swagger UI at /docs | Fetch OpenAPI document and use Swagger to execute documented endpoints | PLANNED |
| R14 | **FastAPI** | Proper error handling | 1 | M03–M06, M09 | Documented 4xx/5xx behavior and safe structured errors | Exercise auth, invalid input, missing IDs, no-path, dependency outage and timeout cases | PLANNED |
| R15 | **Advanced Cypher** | Pathfinding/GDS in ≥2 endpoints | 4 | M05, M06 | Citation shortest-path and PageRank endpoints; Louvain also available | Use real Neo4j/GDS integration tests and live requests; inspect returned path/rank evidence | PLANNED |
| R16 | **Advanced Cypher** | Complex pattern matching | 3 | M05 | Topic/paper/claim/entity cross-paper pattern queries | Compare complex-pattern output with hand-checked fixtures including decoy mentions | PLANNED |
| R17 | **Advanced Cypher** | `WITH`, `UNWIND`, subqueries, aggregations | 2 | M03, M05 | Batch evidence lookup and analytical queries using WITH, UNWIND, subqueries and aggregation | Execute query fixtures and explain deduplication, grouping and subquery behavior | PLANNED |
| R18 | **Optimization** | Optimized queries + benchmarks | 5 | M05, M08 | Bounded parameterized/paginated queries and before/after performance report | Check LIMIT, parameters, subqueries, indexes, pagination and no Cartesian products; compare p50/p95 and query plans on identical data | PLANNED |
| R19 | **GDS & Agentic** | GDS projection + ≥2 algorithms | 2 | M06 | Named in-memory paper projection, weighted PageRank and Louvain | Verify projection nodes/edges/weights/memory and execute both algorithms on fixture and actual corpus | PLANNED |
| R20 | **GDS & Agentic** | ML prediction/classification workflow | 3 | M07 | Graph-feature citation-link model, split manifests, baselines and metric report | Verify labels/split leakage controls; reproduce training and held-out metrics; report insufficient-data gate if blocked | PLANNED |
| R21 | **GDS & Agentic** | LangGraph / GraphRAG / NL-to-Cypher | 4 | M04, M06 | Genuine LangGraph agent with state, conditional routing, typed tools, prompts and structured answers | Inspect implementation and actual multi-tool trace; exercise successful retrieval and routing paths | PLANNED |
| R22 | **GDS & Agentic** | LLM reliability and guardrails | 4 | M03, M04, M08 | Schema/quote checks, query-plan validation, confidence/status policy, budgets and reliability evaluation | Test invalid/raw Cypher rejection, prompt injection, unsupported citations, hypotheses and abstention; manually score source support | PLANNED |
| R23 | **Schemas & Modeling** | Neo4j graph diagram | 2 | M01, M10 | Editable graph-schema diagram plus export with directions/properties | Compare final diagram with actual schema and verify provenance paths | PLANNED |
| R24 | **Schemas & Modeling** | System architecture diagram | 2 | M02, M10 | Editable system diagram plus export showing services, ports and flows | Compare with running Compose services, network bindings and ingestion/agent data flows | PLANNED |
| R25 | **Schemas & Modeling** | Modeling rationale + anti-genericity appendix | 3 | M01, M10, M11 | Modeling rationale and same-prompt generic AI baseline comparison appendix | Retain baseline artifact and student-reviewed differences; orally defend node/property/relationship/index choices | PLANNED |
| R26 | **Documentation** | Complete README + screenshots | 3 | M10 | Complete root README with genuine screenshots and setup/API/data/modeling evidence | Teammate follows from fresh checkout; check screenshots/links against running application | PLANNED |
| R27 | **Documentation** | Demonstration notebook | 2 | M06–M10 | demo.ipynb with graph exploration, visualizations, GDS/ML and agent outputs | Execute notebook top to bottom against declared snapshot; inspect real outputs | PLANNED |
| R28 | **Clean Code** | `.pylintrc`, pylint ≥ 9.5, `make lint` | 2 | M02, M09 | .pylintrc following professor rules and functional make lint | Read linked rules first; retain actual pylint output showing at least 9.5/10 and exit status | PLANNED |
| R29 | **Clean Code** | PEP 8 + clean architecture | 1 | M02–M09 | PEP 8 code, coherent modules and useful object-oriented design | Lint/style checks and substantive peer review of boundaries, naming and complexity | PLANNED |
| R30 | **Clean Code** | Docstrings | 1 | M03–M09 | Docstrings for modules, public functions/classes and non-obvious query/algorithm behavior | Review docstrings against actual interfaces and run configured docstring lint checks | PLANNED |
| R31 | **Makefile** | Required commands | 1 | M02, M09 | Makefile: help, install, run, docker-run, test, lint, clean; useful venv/build extras | Inspect command coverage against specification; no placeholder success targets | PLANNED |
| R32 | **Makefile** | Commands functional | 1 | M09, M11 | Working Make targets and clear make help | Execute every required target in a disposable workspace; verify effects and exit codes, including non-destructive clean scope | PLANNED |
| R33 | **Makefile** | Usage documented | 1 | M10 | README Make usage with prerequisites and expected behavior | Follow documented commands and compare them with make help | PLANNED |
| R34 | **Tests** | Unit/API/Neo4j tests | 3 | M03–M09 | Pytest unit/API/real Neo4j connectivity tests | Run full suite with required services, inspect results and distinguish mocked/model-live cases | PLANNED |
| R35 | **Tests** | Container health checks | 2 | M02, M09 | Neo4j/FastAPI container health checks and tests; model readiness check | Observe healthy startup and controlled dependency-failure readiness; check recovery and timeouts | PLANNED |
| R36 | **Tests** | Cypher tests | 2 | M03, M05, M09 | Cypher constraint, traversal, analytical-query and GDS integration tests under make test | Run make test and verify these tests executed against a real fixture database | PLANNED |
| R37 | **Tests** | Coverage ≥ 60% | 2 | M09 | Coverage configuration/report with overall app coverage at least 60% | Run coverage measurement; inspect denominator/exclusions and failure threshold | PLANNED |
| R38 | **Tests** | All tests pass | 1 | M09, M11 | Passing complete test run and generated coverage artifacts | Retain actual exit code, counts and report from the final revision; missing/skipped required tests remain a gap | PLANNED |
| R39 | **SE Best Practices** | Lint workflow | 1 | M02, M09 | GitHub Actions lint workflow on push/PR | Inspect workflow triggers and actual run logs/status for a concrete revision | PLANNED |
| R40 | **SE Best Practices** | Test workflow | 1 | M02, M09 | GitHub Actions test workflow with coverage artifacts | Inspect successful real run, integration-service setup and coverage artifact; record excluded live-model checks | PLANNED |
| R41 | **SE Best Practices** | README badges | 1 | M09, M10 | README build/test/coverage badges linked to real workflows/reports | Open each badge destination and verify status belongs to this repository/revision | PLANNED |
| R42 | **SE Best Practices** | Code reviews | 1 | M00–M11 | PR review evidence with at least 2 constructive comments per PR | Audit PR URLs/screenshots and reviewer comments, responses and resulting changes | PLANNED |
| R43 | **SE Best Practices** | Reverse proxy or authentication | 3 | M03, M09 | Authentication on sensitive corpus-import endpoint | Test missing/invalid/valid credentials, fail-closed configuration and redacted logs | PLANNED |
| R44 | **SE Best Practices** | `EXPLAIN` / `PROFILE` demonstration | 2 | M05, M08 | Strategic index demonstration using EXPLAIN/PROFILE and measured comparison | Capture before/after plans, operator/index use, rows/db hits and latency with matching results | PLANNED |
| R45 | **Git** | Branch workflow | 2 | M00–M11 | Stable main plus at least 2 active branches and member feature branches | Inspect git branch/remote history and GitHub PR branch usage; branch-name proposals do not count | PLANNED |
| R46 | **Git** | Proper `.gitignore` | 1 | M02, M09 | Existing .gitignore, audited for secrets, caches, PDFs and generated data | Check ignore behavior on representative paths and audit tracked files/history; existing file alone is not full verification | NOT VERIFIED |
| R47 | **Git** | Balanced contributions | 3 | M00–M11 | Reasonably balanced substantive contributions and contribution table | Audit git shortlog, GitHub Contributors, task ownership and substance of changes; calculate actual percentages | PLANNED |
| R48 | **Git** | ≥1 substantial merged PR/member | 3 | M00–M11 | At least one substantial merged PR for every member | Audit per-member merged PR URLs, scope, review and tests; do not count cosmetic-only work as substantial | PLANNED |
| R49 | **Git** | Clear commit messages | 1 | M00–M11 | Clear descriptive commit messages using appropriate prefixes | Review actual git log for intent/scope; preserve honest authorship | PLANNED |

### Exact section totals (planned coverage, not awarded points)

| Professor section | Points |
| --- | ---: |
| Core Technical Components | 25 |
| Advanced Neo4j & Agentic | 27 |
| Architecture, Documentation & Clean Code | 16 |
| Makefile & Automation | 3 |
| Tests & Quality | 10 |
| Software Engineering Best Practices | 9 |
| Collaboration & Git Management | 10 |
| **Total** | **100** |

Category subtotals: Docker 9; Neo4j 10; FastAPI 6; Advanced Cypher 9; Optimization 5; GDS & Agentic 13; Schemas & Modeling 7; Documentation 5; Clean Code 4; Makefile 3; Tests 10; SE Best Practices 9; Git 10. There are no unmapped checklist rows. Implementation and external evidence remain outstanding across the rubric.

## Required delivery contents and documentation acceptance

Future delivery must include source code under `app/`, ingestion/analytics scripts under `scripts/`, `tests/`, `docker-compose.yml`, the custom-service Dockerfile, `.env.example`, `requirements.txt` with reproducible pins, `Makefile`, `.pylintrc`, `demo.ipynb` and a comprehensive root README. Include a dedicated `.venv` workflow; use object-oriented design where justified. These artifacts are planned, not created by this task.

The README must contain description/use cases, installation and execution, dataset sources and licensing/version notes, API examples, actual screenshots, graph schema and system architecture with ports/flows, model/index/algorithm rationale, LLM guardrails and evaluation limits, Make usage, public registry link, real badges and team contribution/PR evidence. The notebook must execute graph exploration/visualization, evidence-backed agent examples, GDS and ML outputs without invented results.

Provide editable draw.io graph-schema and system-architecture sources plus exports. Mermaid planning diagrams are preliminary aids; they do not prove the deployed architecture. The anti-genericity appendix must preserve the same-description generic AI baseline, compare it to the student-reviewed final model and explain deliberate differences (especially Claim provenance, method mentions versus use, aliases and derived citations).

## Live-demonstration script and acceptance

1. On the target machine, show repository version, required environment placeholders, image digests and actual corpus snapshot/counts. Start from documented reproducible setup; distinguish model-download preparation from clean application startup.
2. Run `make help`, `make lint`, `make test` and `make docker-run`, retain outputs and show health status. Explain failed or skipped checks rather than replacing them with saved successes.
3. Show Neo4j connectivity, constraints/indexes, Swagger `/docs`, validated endpoint responses and authenticated-import rejection.
4. Demonstrate a directed citation path with source pages, a topic comparison query and real PageRank/Louvain output. Explain projection weights and limits.
5. Ask a source-supported question that needs multiple LangGraph tools; expose evidence and tool sequence. Trigger a separate invalid/unsafe LLM-output case and show guardrail rejection/abstention.
6. Present the ML split/leakage controls, measured results versus baselines and a prediction visibly labeled as a hypothesis. If incomplete, state the gap.
7. Show measured before/after query performance, actual registry image, contribution history and substantial merged PRs with review comments. Every student explains a major technical choice and its drawback.

## Risks, gates and professor penalties

No required local source document is missing. Open inputs: student approvals, team lead/assignments, deadline, hardware/model budget, annotation capacity, registry destination, precise compatible versions and sufficient verified ML labels. The linked external pylint rules could not be retrieved during planning; inspect the original link or obtain the professor's copy before implementing lint configuration. Candidate paper landing pages were checked, but PDFs were not downloaded or parsed.

Preserve these exact penalty warnings from the specification in the delivery review: broken required Make commands may incur **−3**; missing `.pylintrc` or pylint below 9.5 may incur **−8**; nonfunctional project up to **−25**; missing functional agentic component **−15**; generic undefended schema up to **−5**; contribution below 10% **−5**; no substantial merged PR **−3 per member**; exposed secrets **−5 per secret or credential file**. Cosmetic-only work may trigger individual re-evaluation; plagiarism can yield **0/100 and an administrative report**. These are separate warnings, not extra rubric rows or a revised 100-point total.

Planning document validation checks criterion coverage, point sums, links and preservation only. It does not verify application correctness, Docker operation, tests, scores, PRs, registry publication or live demonstration.
