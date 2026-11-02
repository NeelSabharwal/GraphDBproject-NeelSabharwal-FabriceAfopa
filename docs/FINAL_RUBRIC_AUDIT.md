# Final rubric audit — 2026-11-02

Exact criteria and allocations are copied from the authoritative checklist: **49 rows, 100 points**. These are evidence statuses, not awarded grades. VERIFIED means the stated local behavior/evidence was observed; scientific usefulness and the professor’s final judgment remain separate. Historical deadline October 23 has passed; no extension/submission is claimed.

| ID | Category | Requirement | Points | Implementation | Actual verification | Status | Remaining action |
|---|---|---|---:|---|---|---|---|
| R01 | **Docker Infra & Services** | `docker-compose.yml` with ≥3 services | 2 | docker-compose.yml | Three functional healthy services; actual status/health logs | VERIFIED | None locally |
| R02 | **Docker Infra & Services** | Proper `Dockerfile` / official image | 2 | Dockerfile; docker/neo4j.Dockerfile | Pinned API and Neo4j/GDS builds completed | VERIFIED | Public GDS redistribution remains separate |
| R03 | **Docker Infra & Services** | `.env.example`, no secrets committed | 2 | .env.example; .gitignore; app/config.py | Known-secret and image-exclusion checks; dummy placeholders only | VERIFIED | Keep operator credentials private |
| R04 | **Docker Infra & Services** | ≥1 image on public registry | 2 | Dockerfile; .dockerignore; docs/IMAGE_PUBLICATION.md; docker/licenses | Local API build, offline smoke and exclusions verified; GHCR command/permission guide prepared; no publication | MISSING | Separate authorization for public source/image distribution, reuse terms, push/public visibility/anonymous pull, actual digest/link |
| R05 | **Docker Infra & Services** | Docker Compose starts cleanly | 1 | Makefile; docker-compose.yml | Bounded startup wait, /health/live and /health/ready both HTTP 200 | VERIFIED | Provision model digests before first API start |
| R06 | **Neo4j Database** | Schema: ≥3 labels, ≥3 relation types | 3 | app/ingestion/graph.py | Live 4 labels and 7 relationship types | VERIFIED | None |
| R07 | **Neo4j Database** | ≥2 constraints | 2 | app/ingestion/graph.py | SHOW CONSTRAINTS: four ID uniqueness constraints | VERIFIED | None |
| R08 | **Neo4j Database** | Appropriate indexes | 2 | app/ingestion/graph.py; scripts/embed_chunks.py | All 11 indexes ONLINE, including chunk_nomic_v1; 153 embeddings | VERIFIED | Corpus growth requires new measured index assessment |
| R09 | **Neo4j Database** | Dataset ingestion script | 2 | scripts/ingest.py; app/ingestion | Existing 3 Papers / 153 Chunks; source/citation/atomicity tests pass | VERIFIED | No unnecessary reimport; fresh API import uses same tested CLI |
| R10 | **Neo4j Database** | Dataset source documented | 1 | corpus/corpus_manifest.json; docs/INGESTION.md | Pinned URLs, versions, PDF hashes and reuse/license notes retained | VERIFIED | Do not redistribute PDFs without rights |
| R11 | **FastAPI** | ≥4 endpoints, ≥3 advanced graph queries | 2 | app/agent/api.py; app/analytics/api.py; app/corpus/api.py | 11 application/health routes; five advanced graph GET routes verified | VERIFIED | None locally |
| R12 | **FastAPI** | Pydantic validation | 2 | app/agent/models.py; app/analytics/models.py; app/corpus/api.py | Invalid IDs, bounds, extra import keys and auth tested | VERIFIED | None |
| R13 | **FastAPI** | Swagger `/docs` works | 1 | app/main.py; docs/screenshots/swagger.png | Real HTTP 200 Swagger page and authentic browser capture | VERIFIED | None |
| R14 | **FastAPI** | Proper error handling | 1 | app/health.py; app/agent/api.py; app/analytics/api.py; app/corpus/api.py | 401/403/409/422/429/503/504 and dependency-failure tests | VERIFIED | Keep operational logs private |
| R15 | **Advanced Cypher** | Pathfinding/GDS in ≥2 endpoints | 4 | app/analytics/api.py | Directed paths plus real PageRank and Louvain endpoints | VERIFIED | None |
| R16 | **Advanced Cypher** | Complex pattern matching | 3 | app/analytics/queries.py; app/agent/tools.py | Reviewed multi-hop citation/shared-entity matches with source bundles | VERIFIED | Tiny graph limits representativeness |
| R17 | **Advanced Cypher** | `WITH`, `UNWIND`, subqueries, aggregations | 2 | app/analytics/queries.py | WITH, UNWIND, CALL subqueries and aggregates exercised by tests/PROFILE | VERIFIED | None |
| R18 | **Optimization** | Optimized queries + benchmarks | 5 | scripts/advanced_graph.py; app/analytics/queries.py | Identical outputs, 2387→281 DB hits; 30 alternating samples; p50 1.580→1.148 ms | VERIFIED | Do not generalize tiny warm-cache latency |
| R19 | **GDS & Agentic** | GDS projection + ≥2 algorithms | 2 | app/analytics/gds.py | 3 nodes / 1 logical .75 edge / 2 directions; live PageRank and Louvain | VERIFIED | GraphRAG isolate retained; arbitrary community IDs |
| R20 | **GDS & Agentic** | ML prediction/classification workflow | 3 | app/ml; scripts/train_graph_ml.py; docs/GRAPH_ML.md | Fixed paper-disjoint pilot, real metrics, majority baseline, leakage tests | VERIFIED | Logistic 0/5; development-visible labels; original 8-paper/96-label target unmet |
| R21 | **GDS & Agentic** | LangGraph / GraphRAG / NL-to-Cypher | 4 | app/agent/workflow.py; app/agent/ollama.py | Real StateGraph conditional routing, schema-constrained Qwen and source-read traces | VERIFIED | CPU latency and answer completeness remain limited |
| R22 | **GDS & Agentic** | LLM reliability and guardrails | 4 | app/agent; tests/test_agent.py; tests/test_agent_path_completion.py | Q14 mutation rejected; page-999/invalid action/hash/quote/budget tests pass | VERIFIED | No claim of semantic entailment or production DB permissions |
| R23 | **Schemas & Modeling** | Neo4j graph diagram | 2 | docs/diagrams/graph-schema.drawio; graph-schema.svg | Editable XML and viewable SVG match four labels/seven relation types | VERIFIED | Students must defend schema choices |
| R24 | **Schemas & Modeling** | System architecture diagram | 2 | docs/diagrams/system-architecture.drawio; system-architecture.svg | Editable XML and SVG match actual services, boundaries and data flow | VERIFIED | None |
| R25 | **Schemas & Modeling** | Modeling rationale + anti-genericity appendix | 3 | docs/ARCHITECTURE.md; docs/DECISIONS.md; docs/DEMONSTRATION.md | Reified claims, alias scopes, source layers and alternatives explicitly explained | VERIFIED | Student oral defense remains unobserved |
| R26 | **Documentation** | Complete README + screenshots | 3 | README.md; docs/screenshots | Merged PR #11; setup/API/screenshots/notebook dependencies and real CI links reviewed | VERIFIED | Public image link awaits authorized publication; CI access requires repository permission |
| R27 | **Documentation** | Demonstration notebook | 2 | demo.ipynb; scripts/execute_notebook.py | All 18 cells executed; final fingerprint unchanged | VERIFIED | Private outputs excluded from public patch |
| R28 | **Clean Code** | `.pylintrc`, pylint ≥ 9.5, `make lint` | 2 | .pylintrc; Makefile | Fresh make lint 9.54/10; all app/scripts; missing-docstring checks now enabled | VERIFIED | Remaining complexity/style findings remain visible |
| R29 | **Clean Code** | PEP 8 + clean architecture | 1 | app; scripts; tests; Makefile | Black formatting executed; layers retain explicit responsibility | VERIFIED | Some large provenance functions still emit refactoring warnings |
| R30 | **Clean Code** | Docstrings | 1 | app; scripts | 52 public docstrings added; module/public AST audit complete; enabled docstring lint has no findings; executable AST unchanged | VERIFIED | Maintain docstrings with future interface changes |
| R31 | **Makefile** | Required commands | 1 | Makefile | help, venv, install, run, docker-build/run, test, lint, format, clean, tree implemented | VERIFIED | Requires Docker, Make and pinned API image |
| R32 | **Makefile** | Commands functional | 1 | Makefile; scripts/workspace.py | Required targets actually invoked; startup race corrected with --wait | VERIFIED | First startup requires model provisioning |
| R33 | **Makefile** | Usage documented | 1 | README.md; Makefile help | Usage and container-managed .venv explained | VERIFIED | None |
| R34 | **Tests** | Unit/API/Neo4j tests | 3 | tests | Fresh complete suite: 358 passed, zero failures, 35.01 s | VERIFIED | One upstream TestClient deprecation warning |
| R35 | **Tests** | Container health checks | 2 | docker-compose.yml; app/health.py | All three service checks; real liveness/readiness HTTP 200 | VERIFIED | Model presence is required for API readiness |
| R36 | **Tests** | Cypher tests | 2 | tests/test_retrieval_graph.py; test_advanced_graph.py; test_mentions.py | Real fixed Cypher, projection guards, transactional rollback/idempotency | VERIFIED | Synthetic fixtures do not establish large-corpus quality |
| R37 | **Tests** | Coverage ≥ 60% | 2 | Makefile; pyproject.toml | Fresh full coverage 94.61%; local and real remote unit/API coverage 75.84% | VERIFIED | Coverage is not semantic correctness |
| R38 | **Tests** | All tests pass | 1 | tests; docs/FINAL_VALIDATION.md | Fresh full suite 358 passed; corrected isolated test mount, earlier seven failures retained in logs | VERIFIED | Recheck after future source changes |
| R39 | **SE Best Practices** | Lint workflow | 1 | .github/workflows/quality.yml | Actual lint jobs succeeded on PR #10/#11 and both main merges; final main score 9.54 | VERIFIED | This uncommitted follow-up awaits its own later remote run |
| R40 | **SE Best Practices** | Test workflow | 1 | .github/workflows/quality.yml | Actual unit-api jobs succeeded on PR #10/#11 and both merges; main 303 passed, 55 deselected, 75.84% | VERIFIED | Live integration remains local; follow-up is not remotely executed yet |
| R41 | **SE Best Practices** | README badges | 1 | README.md | main workflow badge links to actual successful quality.yml; dated local-build and measured remote-coverage badges link to evidence | VERIFIED | Private-repository badge/CI access requires sign-in; build/coverage snapshots are explicitly not live services |
| R42 | **SE Best Practices** | Code reviews | 1 | GitHub PR #4/#5/#8/#9; docs/FINAL_VALIDATION.md | All PRs #1–#11 inspected; substantive #1–#5 review records; #8 one label approval; #7/#9/#10/#11 no returned comments | PARTIAL | Actual student follow-up reviews needed; cannot fabricate pre-merge review history |
| R43 | **SE Best Practices** | Reverse proxy or authentication | 3 | app/corpus/api.py; tests/test_corpus.py | Fail-closed bearer auth; missing/wrong/correct HTTP 401/403/200 observed | VERIFIED | Local shared secret; not production multi-user authorization |
| R44 | **SE Best Practices** | `EXPLAIN` / `PROFILE` demonstration | 2 | scripts/advanced_graph.py; demo.ipynb | Actual EXPLAIN/PROFILE plans, DB counters and no persisted updates | VERIFIED | None |
| R45 | **Git** | Branch workflow | 2 | Existing Git branches/history; handoff instructions | Feature history and merged PRs #10/#11 verified; isolated follow-up from current main | VERIFIED | Review/commit/push this branch only when separately instructed |
| R46 | **Git** | Proper `.gitignore` | 1 | .gitignore; .dockerignore | Private data/secrets excluded; only approved annotation CSV/gold tracked intentionally | VERIFIED | Inspect staged diffs before later authorized commits |
| R47 | **Git** | Balanced contributions | 3 | git shortlog; README contributions | Merged main: Neel 22/Fabrice 11 including merges; non-merge commits 11 each | PARTIAL | Balanced non-merge counts support participation; substantive effort/independence requires human assessment |
| R48 | **Git** | ≥1 substantial merged PR/member | 3 | GitHub PR #4 and #5/#8 | Merged implementation PRs by Neel and evidence/label PRs by Fabrice; final PR #10 Neel and #11 Fabrice confirmed | VERIFIED | AI-assisted package preparation remains disclosed |
| R49 | **Git** | Clear commit messages | 1 | git log; handoff instructions | Current main history includes descriptive core and documentation integration messages | VERIFIED | No commit created by this follow-up |

## Open evidence and penalty risks

- Public registry publication (2 points) is missing. The API-only GHCR procedure and local checks are ready; separate publication authorization, public visibility and real anonymous-pull evidence remain necessary. The private-source repository has no project LICENSE; owners must decide distribution/reuse terms.
- Six real remote quality runs passed, including both final PRs and main merges. New follow-up changes are locally tested but uncommitted; no new remote run is claimed.
- The specification requires at least two constructive comments per PR. Prior review threads exist, but this condition is not demonstrated for every PR; merged final PRs #10/#11 return no review comments.
- ML workflow mechanics are implemented, but the 0/5 result is not useful generalization evidence. Only 15 development-visible labels and three papers exist; the original eight-paper/96-label design remains unmet.
- The instructor may apply −3 for broken required Make commands, −8 for missing/sub-9.5 pylint, up to −25 for nonfunctional startup/endpoints, −15 for no functional agent, and up to −5 for an undefended generic graph. Local checks mitigate these risks; they do not guarantee a grade.
- Contribution below 10% can incur −5; no substantial merged PR can incur −3 per member; cosmetic-only activity may be reevaluated. Existing PR evidence is documented honestly; package upload is not independent authorship.
- Each exposed secret/file can incur −5. Credentials/private artifacts are excluded; maintain that boundary during operator publishing. Plagiarism can incur 0/100 and an administrative report. AI assistance is disclosed and students remain responsible for understanding the work.
- Live academic demonstration, acceptance of late delivery, image-publication authorization and final student review cannot be manufactured by these local artifacts.

Actual logs, failures and final outcomes: [FINAL_VALIDATION.md](FINAL_VALIDATION.md). Historical planning statuses are superseded only by this dated evidence, not by intention.

## Before/after evidence status (not points awarded)

All 49 exact criteria and their original allocations still total 100. Before this
follow-up: **42 VERIFIED / 6 PARTIAL / 1 MISSING**. After: **46 VERIFIED / 2 PARTIAL /
1 MISSING**. R30 (docstrings), R39 (remote lint), R40 (remote tests) and R41 (badges)
now have concrete evidence. R04 (public image) remains MISSING; R42 (reviews) and R47
(substantive contribution assessment) remain PARTIAL. Existing VERIFIED rows retain
their measured scope and limitations; this is not a prediction of the professor's grade.

The unchanged failed ML result remains 0/5 against a 3/5 baseline. Scientific corpus,
labels, original reviews, gold and persisted graph fingerprint are unchanged.
[Follow-up evidence, exact CI URLs and collaboration table](FINAL_VALIDATION.md#rubric-gap-closure-follow-up--2026-11-02).
