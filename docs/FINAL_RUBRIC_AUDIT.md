# Final rubric audit — 2026-11-02

Exact criteria and allocations are copied from the authoritative checklist: **49 rows, 100 points**. These are evidence statuses, not awarded grades. VERIFIED means the stated local behavior/evidence was observed; scientific usefulness and the professor’s final judgment remain separate. Historical deadline October 23 has passed; no extension/submission is claimed.

| ID | Category | Requirement | Points | Implementation | Actual verification | Status | Remaining action |
|---|---|---|---:|---|---|---|---|
| R01 | **Docker Infra & Services** | `docker-compose.yml` with ≥3 services | 2 | docker-compose.yml | Three functional healthy services; actual status/health logs | VERIFIED | None locally |
| R02 | **Docker Infra & Services** | Proper `Dockerfile` / official image | 2 | Dockerfile; docker/neo4j.Dockerfile | Pinned API and Neo4j/GDS builds completed | VERIFIED | Public GDS redistribution remains separate |
| R03 | **Docker Infra & Services** | `.env.example`, no secrets committed | 2 | .env.example; .gitignore; app/config.py | Known-secret and image-exclusion checks; dummy placeholders only | VERIFIED | Keep operator credentials private |
| R04 | **Docker Infra & Services** | ≥1 image on public registry | 2 | Dockerfile; README.md release commands | API image built locally; no public push authorized/performed | MISSING | Authorize and execute public API publication, record real digest/URL |
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
| R26 | **Documentation** | Complete README + screenshots | 3 | README.md; docs/screenshots | Complete setup/API/results/release guide; genuine Swagger/health captures | VERIFIED | Publication URL and remote CI result intentionally absent |
| R27 | **Documentation** | Demonstration notebook | 2 | demo.ipynb; scripts/execute_notebook.py | All 18 cells executed; final fingerprint unchanged | VERIFIED | Private outputs excluded from public patch |
| R28 | **Clean Code** | `.pylintrc`, pylint ≥ 9.5, `make lint` | 2 | .pylintrc; Makefile | make lint scores 9.54/10 across all app and scripts | VERIFIED | Remaining complexity/style warnings are visible, not suppressed |
| R29 | **Clean Code** | PEP 8 + clean architecture | 1 | app; scripts; tests; Makefile | Black formatting executed; layers retain explicit responsibility | VERIFIED | Some large provenance functions still emit refactoring warnings |
| R30 | **Clean Code** | Docstrings | 1 | app; scripts | Module/public boundary docstrings present; historical helper coverage varies | PARTIAL | Expand concise helper docstrings during student maintenance |
| R31 | **Makefile** | Required commands | 1 | Makefile | help, venv, install, run, docker-build/run, test, lint, format, clean, tree implemented | VERIFIED | Requires Docker, Make and pinned API image |
| R32 | **Makefile** | Commands functional | 1 | Makefile; scripts/workspace.py | Required targets actually invoked; startup race corrected with --wait | VERIFIED | First startup requires model provisioning |
| R33 | **Makefile** | Usage documented | 1 | README.md; Makefile help | Usage and container-managed .venv explained | VERIFIED | None |
| R34 | **Tests** | Unit/API/Neo4j tests | 3 | tests | 358 passing unit/API/live Neo4j/GDS/graph/ML cases | VERIFIED | One upstream TestClient deprecation warning |
| R35 | **Tests** | Container health checks | 2 | docker-compose.yml; app/health.py | All three service checks; real liveness/readiness HTTP 200 | VERIFIED | Model presence is required for API readiness |
| R36 | **Tests** | Cypher tests | 2 | tests/test_retrieval_graph.py; test_advanced_graph.py; test_mentions.py | Real fixed Cypher, projection guards, transactional rollback/idempotency | VERIFIED | Synthetic fixtures do not establish large-corpus quality |
| R37 | **Tests** | Coverage ≥ 60% | 2 | Makefile; pyproject.toml | Full suite application coverage 94.61%; CI-equivalent exceeds 60% | VERIFIED | Coverage is statement coverage, not scientific correctness |
| R38 | **Tests** | All tests pass | 1 | tests; docs/FINAL_VALIDATION.md | Full suite 358 passed, zero failures after corrections | VERIFIED | Re-run after operator patch application |
| R39 | **SE Best Practices** | Lint workflow | 1 | .github/workflows/quality.yml | Lint job implemented; local equivalent passes | PARTIAL | Push and observe a real GitHub Actions run |
| R40 | **SE Best Practices** | Test workflow | 1 | .github/workflows/quality.yml | Unit/API coverage job implemented; local equivalent passes | PARTIAL | Push and observe a real GitHub Actions run; live integrations remain local |
| R41 | **SE Best Practices** | README badges | 1 | README.md | Dynamic actual-status workflow badge added; no invented green badge | PARTIAL | Workflow is not yet published/executed remotely |
| R42 | **SE Best Practices** | Code reviews | 1 | GitHub PR #4/#5/#8/#9; docs/FINAL_VALIDATION.md | Real constructive #4/#5 review evidence; inspected #9 has no returned comments | PARTIAL | Ensure ≥2 constructive comments per PR and review the new packages |
| R43 | **SE Best Practices** | Reverse proxy or authentication | 3 | app/corpus/api.py; tests/test_corpus.py | Fail-closed bearer auth; missing/wrong/correct HTTP 401/403/200 observed | VERIFIED | Local shared secret; not production multi-user authorization |
| R44 | **SE Best Practices** | `EXPLAIN` / `PROFILE` demonstration | 2 | scripts/advanced_graph.py; demo.ipynb | Actual EXPLAIN/PROFILE plans, DB counters and no persisted updates | VERIFIED | None |
| R45 | **Git** | Branch workflow | 2 | Existing Git branches/history; handoff instructions | Feature PR history verified; current feat/graph-ml preserved | VERIFIED | Operator must create/review the final integration branches |
| R46 | **Git** | Proper `.gitignore` | 1 | .gitignore; .dockerignore | Private data/secrets excluded; only approved annotation CSV/gold tracked intentionally | VERIFIED | Inspect staged diffs before later authorized commits |
| R47 | **Git** | Balanced contributions | 3 | git shortlog; README contributions | 19 Neel name variants / 10 Fabrice commits including merges | PARTIAL | Counts alone do not establish balanced substantive work; instructor/student review |
| R48 | **Git** | ≥1 substantial merged PR/member | 3 | GitHub PR #4 and #5/#8 | Fetched merged PRs: Neel implementation and Fabrice evidence/label work | VERIFIED | Final packages are AI-assisted, not invented independent authorship |
| R49 | **Git** | Clear commit messages | 1 | git log; handoff instructions | Existing descriptive implementation/review commits inspected | VERIFIED | No final commits created in this task |

## Open evidence and penalty risks

- Public registry publication (2 points) is missing. No public image push was authorized.
- Workflow definitions/local commands are real; remote lint/test runs and the badge outcome are not yet verified.
- The specification requires at least two constructive comments per PR. Prior review threads exist, but this condition is not demonstrated for every PR or the unsubmitted final packages.
- ML workflow mechanics are implemented, but the 0/5 result is not useful generalization evidence. Only 15 development-visible labels and three papers exist; the original eight-paper/96-label design remains unmet.
- The instructor may apply −3 for broken required Make commands, −8 for missing/sub-9.5 pylint, up to −25 for nonfunctional startup/endpoints, −15 for no functional agent, and up to −5 for an undefended generic graph. Local checks mitigate these risks; they do not guarantee a grade.
- Contribution below 10% can incur −5; no substantial merged PR can incur −3 per member; cosmetic-only activity may be reevaluated. Existing PR evidence is documented honestly; package upload is not independent authorship.
- Each exposed secret/file can incur −5. Credentials/private artifacts are excluded; maintain that boundary during operator publishing. Plagiarism can incur 0/100 and an administrative report. AI assistance is disclosed and students remain responsible for understanding the work.
- Live academic demonstration, acceptance of late delivery, image-publication authorization and final student review cannot be manufactured by these local artifacts.

Actual logs, failures and final outcomes: [FINAL_VALIDATION.md](FINAL_VALIDATION.md). Historical planning statuses are superseded only by this dated evidence, not by intention.
