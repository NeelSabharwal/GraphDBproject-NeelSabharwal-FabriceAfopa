# Advanced Cypher and GDS execution

Implemented on `feat/advanced-cypher-gds`, 2026-10-21, under Prompt #7B.
Deadline: October 23, 2026. No paid services or new dependencies.

## Prerequisites and evidence boundaries

The branch initially had a clean working tree at `2a8649b`, including merged PR #7
and reviewed-evidence implementation `b0634ed`. The integration CLI, source-support
validators, review decisions and runbook were present. The real importer was not
rerun. Installed versions were queried: **Neo4j 5.26.32 / GDS 2.13.2**.

Initial real state: 3 Papers, 153 Chunks, 17 Entities, 25 Claims: 20 approved
scientific assertions, 2 approved bibliography assertions and 3 pending LLM claims.
Relationships: PART_OF 153, NEXT 150, MENTIONS 3, SUBJECT 25, OBJECT 25,
SUPPORTED_BY 60, CITES 2. Original-source evidence remains distinct from analytical
similarity, which creates no persisted relationships or scientific claims.

Only human-approved SOURCE_VERIFIED USES / EVALUATED_ON / ADDRESSES assertions with
complete authenticated support bundles and explicitly accepted canonical Entity
identities enter similarity. Pending/rejected assertions and unresolved identities
are excluded. A17 remains unresolved. Rejected alias equivalences are not merged.
The source-support validator preserves all supporting passages, hashes, offsets,
pages, claim IDs and qualifications. A scoped shared identity does not assert
identical experimental settings. Citation support retains work-level/version
qualifications; citing a work does not prove that the pinned target version was read.

The initial persisted-corpus fingerprint (different from the analytical snapshot) is:
`2e9d45407844e5d848d2d8c6e9cf9303d05c723a0a3b829461b7ed2186899af8`.
Final preservation verification is recorded below and in the ignored local reports.

## HTTP interface and demonstration

All five routes are GET operations with fixed parameterized templates. No route
accepts Cypher, changes reviews, refreshes a projection or writes algorithm scores.

| Route | Parameters and result |
| --- | --- |
| `/api/papers/{paper_id}/paths` | Required `target_id`, `max_hops=1..3` (default 3); directed citation path plus every edge's authenticated source support. Missing path returns 200 with `status=unavailable`. |
| `/api/papers/{paper_id}/shared` | Required `target_id`, optional `kind=Method`, `Dataset` or `Task`; Entity IDs, both papers' Claim IDs and complete evidence. |
| `/api/papers/{paper_id}/related` | Positive shared-entity Jaccard scores, contributing IDs and evidence; score descending, Paper ID tie-break. |
| `/api/papers/centrality` | Executes real weighted `gds.pageRank` against the prepared current projection. |
| `/api/papers/communities` | Executes real weighted `gds.louvain` against that same projection. |

The last four support `limit=1..20` (default 20), `offset=0..100` (default 0).
Shared entities sort by Entity ID; centrality sorts by score then Paper ID;
communities by community ID then Paper ID. Analytics compute the full bounded graph
before paginating results. Same-paper exploration/path endpoints return 400;
unknown selected Paper ID 404; invalid IDs/bounds or extra arguments 422; concurrent
API analytics 429; missing/stale projection, invalid evidence or dependency failure
503. Pydantic validates requests and responses, including finite typed scores.

After rebuilding the API and explicitly refreshing its GDS cache, open
`http://localhost:8000/docs`. Try these exact examples in Swagger or a terminal:

```bash
curl --fail 'http://localhost:8000/api/papers/arxiv:2404.16130v1/paths?target_id=arxiv:2004.04906v1&max_hops=3'
curl --fail 'http://localhost:8000/api/papers/arxiv:2004.04906v1/shared?target_id=arxiv:2005.11401v1&kind=Dataset'
curl --fail 'http://localhost:8000/api/papers/arxiv:2004.04906v1/related?limit=1&offset=0'
curl --fail 'http://localhost:8000/api/papers/centrality?limit=3'
curl --fail 'http://localhost:8000/api/papers/communities?limit=3'
```

Demonstration: inspect GraphRAG → RAG → DPR and the two edges' source qualifications;
show DPR/RAG's four named datasets; show the related-paper score and contributing
IDs; compare PageRank with weighted degree; show the Louvain partition and its tiny
scope. Reverse the citation endpoints or set `max_hops=1` to demonstrate honest
unavailability. No LLM invocation is needed for this graph demonstration.

## Projection design, compatibility and lifecycle

Each selected real Paper becomes one vertex. For each Paper, collect distinct
accepted Entity IDs through the approved scientific Claim allowlist. Enumerate
unordered pairs once (`a.id < b.id`), retain nonempty intersections, and weight by
intersection size / union size. Duplicate assertions about one Entity cannot inflate
weight. No raw MENTIONS, PART_OF, NEXT, CITES or ML output enters this projection.

Installed `SHOW FUNCTIONS` / `SHOW PROCEDURES` signatures and an actual temporary
in-memory compatibility probe confirmed the `gds.graph.project` aggregation,
null-target isolated vertices, UNDIRECTED relationship orientation, graph listing,
node/relationship property streaming, drop, algorithm stream/stats/estimation APIs.
These are local GDS 2.13.2 checks; current online examples alone were not treated as
proof of compatibility. Conceptual references: [Cypher projection](https://neo4j.com/docs/graph-data-science/current/management-ops/graph-creation/graph-project-cypher-projection/)
and [Louvain](https://neo4j.com/docs/graph-data-science/current/algorithms/louvain/).

Virtual integer indices map the sorted Paper IDs into GDS without creating database
nodes. One input row per logical undirected pair becomes two GDS adjacency entries.
Null-target rows preserve isolates. An entirely edgeless graph requests no named
relationship type and omits the absent weight property in algorithm configuration;
all vertices remain. Edgeless modularity uses a documented zero convention.

Names contain a corpus-scope hash and the full analytical SHA-256 fingerprint of
source/review/identity state. Before serving analytics, recompute that snapshot and
check catalog vertices, IDs, orientation, weights and size. Recheck source state
after execution. Missing or changed state returns 503 until explicit operator
refresh. This is a bounded local cache, not a cross-transaction database snapshot;
concurrent administrative changes must not be made during a demonstration.

Limits: 16 Papers, 128 approved scientific Claims, 120 unordered pairs, 5-second
individual database query timeout, concurrency 1, one API algorithm request at a
time, 64 MiB actual projection size and 64 MiB algorithm estimate. Creation is
bounded by vertex/edge caps; this aggregation does not provide an exact precreation
estimate. The actual created size is checked immediately; supported algorithm
estimates gate execution. The API lock is per process; the current deployment has
one Uvicorn process. These are not guarantees for an expanded corpus or a multiworker
deployment. Read routing is not database authorization: the application capability
boundary is the finite read/procedure registry, and catalog mutation exists only
in the local operator class.

Reproducible commands from the repository root (existing Compose configuration
supplies credentials without printing them):

```bash
docker compose build api
docker compose up -d --no-deps api
docker compose exec -T api python -m scripts.advanced_graph refresh
docker compose exec -T api python -m scripts.advanced_graph status
docker compose exec -T api python -m scripts.advanced_graph pagerank
docker compose exec -T api python -m scripts.advanced_graph louvain
docker compose exec -T api python -m scripts.advanced_graph benchmark
```

After Neo4j restart the in-memory catalog is lost; run `refresh` again. Refresh reuses
a valid existing graph or replaces obsolete graphs only in the selected corpus's
managed namespace. To remove a cache deliberately, copy its exact name from `status`
and use `python -m scripts.advanced_graph drop --name EXACT_NAME` in the API container.
No arbitrary names, prefix-wide deletion or HTTP management route is supported.

## Actual three-paper results

Analytical fingerprint:
`83b7833f098a4b9ff5490055ba9e5ad3759e08b33413c80e9b61d344649dfc85`.
Projection:
`research_sim_b04e3853184b_83b7833f098a4b9ff5490055ba9e5ad3759e08b33413c80e9b61d344649dfc85`.

Actual creation: **3 vertices, 1 logical undirected pair, 2 GDS adjacency entries**,
4,919,744 catalog bytes, 235 ms projection time. The only pair is DPR–RAG:
6 shared Entities / 8 union Entities = **0.75**. GraphRAG is isolated. Shared IDs:
`dataset:curatedtrec`, `dataset:natural-questions`, `dataset:triviaqa`,
`dataset:webquestions`, `method:bert-base`,
`task:open-domain-question-answering`. Explanation records include all contributing
source/target Claim IDs. This was computed from the live approved set, not copied
from the historical expected fixture.

Both algorithms use `relationshipWeightProperty=weight`, `concurrency=1`, and
`logProgress=false`. PageRank: `dampingFactor=0.85`, `maxIterations=100`,
`tolerance=1e-7`. Louvain: `maxLevels=10`, `maxIterations=10`, `tolerance=0.0001`.
No unsupported random seed parameter is supplied.

| Paper | PageRank | Weighted degree | First Louvain community | Size |
| --- | ---: | ---: | ---: | ---: |
| DPR (`arxiv:2004.04906v1`) | 0.9999994772616189 | 0.75 | 1 | 2 |
| RAG (`arxiv:2005.11401v1`) | 0.9999994772616189 | 0.75 | 1 | 2 |
| GraphRAG (`arxiv:2404.16130v1`) | 0.15000000000000002 | 0 | 2 | 1 |

PageRank stats: 88 iterations, converged true, 116 ms compute. The separate streamed
result took 109.04 ms; full source-validation/estimation/stats/stream operation
730.49 ms. Estimated algorithm allocation: 592 bytes, excluding stored projection
and Neo4j overhead. Scores are GDS's returned values, not normalized probabilities.
DPR and RAG tie just as weighted degree does. This is navigation prominence in a
scoped similarity graph, not scientific quality, authority or citation impact.

Three Louvain runs returned the same partition: {DPR, RAG}, {GraphRAG}, with
modularity **0.0**, one level and two communities. Stats compute times: 42 / 59 /
36 ms; stream times: 77.86 / 39.76 / 44.89 ms; complete operation times: 646.15 /
533.08 / 505.37 ms. Estimated allocation: 2,105–560,128 bytes. `stats` and `stream`
are separate executions with identical settings, so the response also recomputes
weighted modularity from the actual full streamed partition. These three observations
do not prove general stability. IDs are arbitrary and the partition simply mirrors
connectivity here. GraphRAG's use of **Leiden** is a source fact; this implementation's
**Louvain** is a separate project analytics choice.

## Cypher optimization and measurements

Fixed templates use variable-length directed patterns for citation paths, shared
Entity joins, `WITH`, `UNWIND`, per-Paper subqueries, distinct-set aggregation,
explicit ordering and bounded pagination. Existing Paper-ID uniqueness indexes are
used; no new persisted schema changes were necessary.

The baseline paired papers first, repeatedly joining their Claims and multiplying
intermediate rows. The implementation aggregates each Paper's distinct approved
Entity set once, then enumerates bounded pairs. Both returned identical real-corpus
results. Timing setup: one local async Bolt client, no LLM, five warmups per query,
30 alternating-order samples per query. Timings cover the Bolt query, not complete
source validation or HTTP serialization.

| Query | PROFILE operator DB-hit sum | p50 ms | p95 ms |
| --- | ---: | ---: | ---: |
| Repeated per-pair Claim join baseline | 2,387 | 6.917 | 10.763 |
| Aggregate-before-pair implementation | 281 | 4.421 | 5.674 |

EXPLAIN and PROFILE were also executed for citation paths (118 DB hits) and shared
datasets (159 DB hits). Plans include `NodeUniqueIndexSeek` for Paper IDs;
`VarLengthExpand(All)` for bounded paths; distinct/eager aggregation and subquery
application for set construction. Full operator trees, arguments, row counts and
all timing samples are in `benchmark.json`. This is a warm three-paper, 20-approved-
scientific-Claim benchmark: noise, caching and tiny outputs limit generalization.
Pagination bounds response size; it does not avoid full bounded GDS computation.

## Verification and remaining work

Execution reports are ignored local artifacts under `data/processed/advanced-graph/`:
`baseline.json`, `compatibility-synthetic.json`, `refresh.json`, `pagerank.json`,
`louvain-1.json` through `louvain-3.json`, `benchmark.json`, and test logs.
Automated tests cover real paths/datasets, errors and bounds, read-only HTTP
capabilities, absent/stale/corrupt projections, duplicate Claims, pending/rejected
status, unresolved aliases, isolates, typed results and both installed algorithms.
Synthetic integration tests use UUID-scoped fixtures and clean them up; they never
change the three real papers' review decisions.

Development failures are retained: the first run found a synthetic duplicate-ID
fixture setup error; the second found the all-isolate GDS relationship-type issue.
Both were corrected rather than suppressing their tests. Final execution results
are appended after verification.

No ML training, corpus expansion, student approval changes or evaluation-gold access
was introduced. The three-paper graph demonstrates implementation and evidence
boundaries, not meaningful research communities or general ranking quality. ML still
requires independent source-reviewed chunk labels, defensible graph features,
baselines and a held-out whole-paper split. CI/registry/review/submission requirements
must be checked separately; this slice does not establish completion of the rubric.

### Final execution checks

- `make test`: **300 passed, 0 failed, 1 warning in 45.58 s**; application coverage
  **96%** (1,867 statements, 82 missed). The warning is Starlette's use of the
  deprecated AnyIO `BlockingPortal` alias. No tests were skipped. See
  `test-run-3.log` and `data/processed/coverage.xml`.
- `docker compose build api` and `docker compose up -d --no-deps api`: succeeded.
  Neo4j/Ollama were not restarted. All three services are healthy.
- `make health`: live 200 `ok`; ready 200 `ready`, both `neo4j_gds` and `ollama` `ok`.
- Live HTTP smoke: all five domain endpoints, Swagger and OpenAPI returned 200.
  Measured HTTP times: path **101.00 ms**, shared datasets **175.60 ms**, related
  **149.73 ms**, PageRank **470.44 ms**, Louvain **428.13 ms**. These are single
  local observations, not latency percentiles or a load test. Reverse/one-hop paths
  were unavailable; unknown paper 404, identical endpoints 400, excessive limit and
  extra Cypher argument 422; pagination returned the requested one result.
- Final original-corpus counts and fingerprint exactly match the initial values
  above. The catalog contains only the intended three-node/two-adjacency projection;
  synthetic test projections were cleaned up. No real evidence importer, review
  mutation, persisted analytical edge or algorithm-property write was executed.
- `git diff --check`: passed. Professor requirements, teammate evidence/reviews,
  corpus files and gold labels were not changed. No branch change, commit or push.

Additional local reports: `api-build.log`, `api-start.log`, `health.log`,
`services.txt`, `http-smoke.json` and `final-state.json`. These are ignored generated
artifacts, not source evidence or review approvals. Reproduction after future source
or review changes may produce a different snapshot and must explicitly refresh it.
