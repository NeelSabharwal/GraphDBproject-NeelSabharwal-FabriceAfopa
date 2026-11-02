# Final rubric audit — 2026-11-02

Exact criteria and allocations are copied from the authoritative checklist: **49 rows, 100 points**. These are evidence statuses, not awarded grades. VERIFIED means the stated local behavior/evidence was observed; scientific usefulness and the professor’s final judgment remain separate. Historical deadline October 23 has passed; no extension/submission is claimed.

| ID | Category | Requirement | Points | Implementation | Actual verification | Status | Remaining action |
|---|---|---|---:|---|---|---|---|
| R01 | **Docker Infra & Services** | `docker-compose.yml` with ≥3 services | 2 | docker-compose.yml | Three functional healthy services; actual status/health logs | VERIFIED | None locally |
| R02 | **Docker Infra & Services** | Proper `Dockerfile` / official image | 2 | Dockerfile; docker/neo4j.Dockerfile | Pinned API and Neo4j/GDS builds completed | VERIFIED | Public GDS redistribution remains separate |
| R03 | **Docker Infra & Services** | `.env.example`, no secrets committed | 2 | .env.example; .gitignore; app/config.py | Known-secret and image-exclusion checks; dummy placeholders only | VERIFIED | Keep operator credentials private |
| R04 | **Docker Infra & Services** | ≥1 image on public registry | 2 | .github/workflows/publish-api.yml; scripts/release_preflight.py; docs/IMAGE_PUBLICATION.md | [Public package](https://github.com/users/NeelSabharwal/packages/container/package/graphdbproject-neelsabharwal-fabriceafopa-api); anonymous tag/digest pull confirmed; offline live/docs 200; [publication evidence](IMAGE_PUBLICATION.md) | VERIFIED | None for public API image; source repository remains private |
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
| R26 | **Documentation** | Complete README + screenshots | 3 | README.md; docs/screenshots | Merged PRs #11/#12; final setup/navigation/screenshots/notebook dependency and CI links checked | VERIFIED | Public image link verified; private CI requires repository access |
| R27 | **Documentation** | Demonstration notebook | 2 | demo.ipynb; scripts/execute_notebook.py | Final 22 cells executed; actual directed path and PageRank SVG rendered; graph fingerprint unchanged | VERIFIED | Private executed output remains ignored |
| R28 | **Clean Code** | `.pylintrc`, pylint ≥ 9.5, `make lint` | 2 | .pylintrc; Makefile | Release follow-up lint 9.56/10; all app/scripts; missing-docstring checks enabled | VERIFIED | Remaining complexity/style findings visible |
| R29 | **Clean Code** | PEP 8 + clean architecture | 1 | app; scripts; tests; Makefile | Black formatting executed; layers retain explicit responsibility | VERIFIED | Some large provenance functions still emit refactoring warnings |
| R30 | **Clean Code** | Docstrings | 1 | app; scripts | 52 public docstrings added; module/public AST audit complete; enabled docstring lint has no findings; executable AST unchanged | VERIFIED | Maintain docstrings with future interface changes |
| R31 | **Makefile** | Required commands | 1 | Makefile | help, venv, install, run, docker-build/run, test, lint, format, clean, tree implemented | VERIFIED | Requires Docker, Make and pinned API image |
| R32 | **Makefile** | Commands functional | 1 | Makefile; scripts/workspace.py | Required targets actually invoked; startup race corrected with --wait | VERIFIED | First startup requires model provisioning |
| R33 | **Makefile** | Usage documented | 1 | README.md; Makefile help | Usage and container-managed .venv explained | VERIFIED | None |
| R34 | **Tests** | Unit/API/Neo4j tests | 3 | tests | Final complete suite: 358 passed, zero failures, 44.61 s | VERIFIED | One upstream TestClient deprecation warning |
| R35 | **Tests** | Container health checks | 2 | docker-compose.yml; app/health.py | All three service checks; real liveness/readiness HTTP 200 | VERIFIED | Model presence is required for API readiness |
| R36 | **Tests** | Cypher tests | 2 | tests/test_retrieval_graph.py; test_advanced_graph.py; test_mentions.py | Real fixed Cypher, projection guards, transactional rollback/idempotency | VERIFIED | Synthetic fixtures do not establish large-corpus quality |
| R37 | **Tests** | Coverage ≥ 60% | 2 | Makefile; pyproject.toml | Final full coverage 94.61%; local unit/API and merged-main remote unit/API 75.84% | VERIFIED | Coverage is not semantic correctness |
| R38 | **Tests** | All tests pass | 1 | tests; docs/FINAL_VALIDATION.md | Final complete suite 358 passed; notebook 22 cells executed; no new failures | VERIFIED | Earlier isolated-mount failures remain documented historically |
| R39 | **SE Best Practices** | Lint workflow | 1 | .github/workflows/quality.yml | Merged-main 9dc29fe quality run 41514134025 lint succeeded: 9.56/10 | VERIFIED | Documentation branch CI is checked after push; local lint 9.56 is separate |
| R40 | **SE Best Practices** | Test workflow | 1 | .github/workflows/quality.yml | Merged-main run 41514134025: 318 passed, 55 deselected, 75.84%, 13.97 s | VERIFIED | 55 real-dependency tests run locally; acceptance-branch results reported with its PR |
| R41 | **SE Best Practices** | README badges | 1 | README.md | main quality.yml badge and dated local-build / b782bbf remote-coverage badges point to actual evidence | VERIFIED | Private repository CI/badges can require sign-in; snapshots are not live coverage services |
| R42 | **SE Best Practices** | Code reviews | 1 | GitHub PRs #1–#13; docs/FINAL_VALIDATION.md | Earlier #1–#5 evidence retained; 18 genuine post-merge comments on #7–#13 inspected and linked; #8 earlier label approval separate | PARTIAL | Two constructive comments per PR not fully evidenced across all PRs; retrospective comments are not pre-merge reviews |
| R43 | **SE Best Practices** | Reverse proxy or authentication | 3 | app/corpus/api.py; tests/test_corpus.py | Fail-closed bearer auth; missing/wrong/correct HTTP 401/403/200 observed | VERIFIED | Local shared secret; not production multi-user authorization |
| R44 | **SE Best Practices** | `EXPLAIN` / `PROFILE` demonstration | 2 | scripts/advanced_graph.py; demo.ipynb | Actual EXPLAIN/PROFILE plans, DB counters and no persisted updates | VERIFIED | None |
| R45 | **Git** | Branch workflow | 2 | Existing Git branches/history; handoff instructions | Merged PRs #10/#11/#12; isolated feat/final-acceptance from main b782bbf; original checkout preserved | VERIFIED | Final PR merge requires user confirmation |
| R46 | **Git** | Proper `.gitignore` | 1 | .gitignore; .dockerignore | Private data/secrets excluded; only approved annotation CSV/gold tracked intentionally | VERIFIED | Inspect staged diffs before later authorized commits |
| R47 | **Git** | Balanced contributions | 3 | git shortlog; README contributions | Merged main b782bbf: Neel 24 / Fabrice 11 commits including merges; non-merge 12 / 11; author spelling variants retained | PARTIAL | Counts do not establish balanced substantive effort or independent authorship; human assessment remains |
| R48 | **Git** | ≥1 substantial merged PR/member | 3 | GitHub PR #4 and #5/#8 | Merged implementation PRs by Neel and evidence/label PRs by Fabrice; final PR #10 Neel and #11 Fabrice confirmed | VERIFIED | AI-assisted package preparation remains disclosed |
| R49 | **Git** | Clear commit messages | 1 | git log; handoff instructions | Main includes descriptive core/docs/rubric commits; final branch uses genuine configured identity | VERIFIED | No history rewritten or authorship manufactured |

## Open evidence and penalty risks

- R04 (2 allocated points) is now **VERIFIED**: independent anonymous pull/tag resolution
  returned the published digest, and offline live/docs checks passed. See the
  [publication record](IMAGE_PUBLICATION.md). Source privacy remains unchanged.
- Latest merged-main quality evidence: [run 41514134025](https://github.com/NeelSabharwal/GraphDBproject-NeelSabharwal-FabriceAfopa/actions/runs/41514134025),
  318 tests / 75.84% coverage / pylint 9.56. Local checks and the documentation
  branch CI are reported separately.
- R42 remains PARTIAL. Eighteen actual post-merge comments on #7–#13 are now
  [linked with timestamps](FINAL_VALIDATION.md#retrospective-review-evidence-inspected-on-2026-11-02).
  They improve documented discussion but cannot establish pre-merge reviews or
  two constructive comments across every PR. No new approvals are inferred.
- R47 remains PARTIAL: balanced non-merge counts support participation but do not
  determine substantive effort, independence or the professor's assessment.
- ML mechanics are verified, but logistic 0/5 versus majority 3/5 is weak evidence.
  Only 15 development-visible labels and three papers exist. The original larger
  eight-paper/96-label design remains unmet; no retraining or corpus expansion occurred.
- Live oral defense, understanding of modeling choices, academic submission and
  acceptance after the historical October 23 deadline cannot be verified by code.
  Diagrams, demonstration script/notebook and contribution records are prepared.
- Course penalties remain applicable: broken required Make commands −3; missing or
  sub-9.5 pylint −8; nonfunctional project up to −25; no functional agent −15;
  undefended generic schema up to −5; contribution below 10% −5; no substantial merged
  PR −3/member; exposed secrets −5/file; plagiarism can result in 0/100. These checks
  are evidence, not a promise about the instructor's decision. AI assistance is disclosed.

## Final evidence totals — not awarded marks

All **49 criteria and their exact allocations total 100 points**. The table's
requirement text and point values were compared row-for-row with the professor's
unchanged checklist.

| Evidence status | Rows | Allocated points |
|---|---:|---:|
| VERIFIED within stated scope | 47 | 96 |
| PARTIAL: R42, R47 | 2 | 4 |
| BLOCKED | 0 | 0 |
| MISSING | 0 | 0 |
| Total | 49 | 100 |

Before PR #12: 42 VERIFIED / 6 PARTIAL / 1 MISSING. After PR #12: 46 VERIFIED /
2 PARTIAL / 1 MISSING. Historical final acceptance retained the 46 verified rows and changed
R04 to BLOCKED to explain authorization and the remaining gates. It also closes an
overlooked notebook evidence gap: the previous text-only exploration now has two
executed visualizations derived from live results. No additional grading credit is
self-awarded, and blocked/partial allocations are not counted as verified points.

[Final command results, graph invariants, CI and cleanup](FINAL_VALIDATION.md#final-acceptance--2026-11-02).
The scientific corpus, approval/label records, gold and failed ML result remain unchanged.

## Historical GHCR release preparation — 2026-11-02

The following pre-publication snapshot is superseded by the confirmed public pull below.

PR #13 is merged at d35cd2e. The dedicated release PR adds manual/main-only publishing
with contents-read/packages-write permissions and a tested fail-closed preflight.
105 Debian binaries map to 73 source packages; 245 selected source archives were
actually downloaded, size/hash checked and bundled into the local release candidate.
Orjson and the identified Python/MPL source gaps are resolved; all three wheel
libquadmath source mappings are established by official RPM/ELF comparisons and
matching bundled source RPMs. The final local gate passes. No public push/digest/anonymous pull is claimed.
R04 therefore remains BLOCKED; totals stay **46 VERIFIED / 2 PARTIAL / 1 BLOCKED**,
allocated **94 / 4 / 2 points**, not grades. Reviews and contribution assessment remain
partial. Current offline checks are distinguished from the previous full live suite
in [FINAL_VALIDATION.md](FINAL_VALIDATION.md); no scientific experiment was rerun.

## Confirmed GHCR publication — 2026-11-02

PR #14 merged at `9dc29fe2bac68abf12bff335ad2e5cdc061c3393`. The manual publication
workflow succeeded; its public SHA tag resolves to registry digest
`sha256:9b22b9a0a1396b7fc3485574a9a6a19a35b2316f7d0740bcc4435504912b73cf`.
Independent anonymous pull and offline liveness/Swagger passed, source repository
privacy was confirmed, and README now links the real public package. R04 changes
from BLOCKED to VERIFIED. Current totals: **47 VERIFIED / 2 PARTIAL / 0 BLOCKED /
0 MISSING**, allocated **96 / 4 / 0 / 0 points**, not awarded marks. R42 and R47
remain partial for the reasons above. No scientific data, review or frozen ML result changed.
