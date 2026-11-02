# Final local validation — 2026-11-02

This report records actual local work, not a grade, a GitHub Actions result, publication
or submission. The October 23 deadline has passed. All operations used local/free tooling.
Private reports are under `data/processed/final-delivery-20261102/`; source PDFs, exports,
model weights, backups and credentials are excluded from the public packages.

## Initial and final protected state

Branch remained `feat/graph-ml`; HEAD remained
`86c9540ae9fcc35a976012da39d947b2af07179d`. Initial tracked tree was clean with two
untracked input reports: `ML_FEASIBILITY_AUDIT.md` and `ML_MENTIONS_FEASIBILITY.md`.
Both are preserved unchanged and included as historical core-package evidence.
An unrelated `.vscode/settings.json` appeared during work and is preserved/excluded.
No commit, push, merge, branch switch or public image publication was performed.

Initial full suite: **300 passed**, one warning, **96% rounded coverage**, 31.77 s.
Initial graph fingerprint:
`a847ebb5017a08830c281a64afbdba68a278d208e88f499ac7bde54628594682`.
After the sole authorized real mutation (145 MENTIONS), full fingerprint:
`0a17d318be0066b5b7fb20a88e1821586cc3135c07dbbd9a27012ebfe363d62f`.
Excluding precisely those owned edges reproduces the initial fingerprint. Neo4j
nodes, original relationships, review history, aliases and embeddings are unchanged.

| Actual graph item | Count |
|---|---:|
| Paper / Chunk / Entity / Claim | 3 / 153 / 17 / 25 |
| SOURCE_VERIFIED / EXTRACTED Claims | 22 / 3 |
| PART_OF / NEXT | 153 / 150 |
| SUBJECT / OBJECT / SUPPORTED_BY | 25 / 25 / 60 |
| CITES / MENTIONS | 2 / 148 |
| Chunks with embeddings | 153 |

Actual Neo4j **5.26.32**, GDS **2.13.2**. Four uniqueness constraints and all 11 indexes
(including VECTOR `chunk_nomic_v1`) are ONLINE. GraphRAG → RAG → DPR is a real directed
path, with original bibliography source bundles and work-level/version qualifications.
Shared DPR/RAG named datasets are Natural Questions, TriviaQA, WebQuestions and
CuratedTREC. No citation or scientific claim was invented or re-approved.

## Backup and mention application

The actual volume was `ai-research-graphrag_neo4j_data`. Offline archive:
`neo4j-before-mentions-20261102T130826Z.tar.gz` in the private delivery directory,
10,438,771 bytes, 132 entries, validated gzip/tar contents. SHA-256:
`2952f99c907a4f16f2f3bcf0a26f779846898b7f82f4c669d4a3d6412a19a8cb`.
The receipt and sidecar checksum are retained. The first helper-image attempt failed
before data copying; a present helper image resolved it before any application.

The frozen proposal/policy hashes matched exactly, all 153 source Chunks were
revalidated, and 20 matcher/import tests passed before application. One transaction
created 145 mechanical occurrences. Replay proposes zero new / 145 reused. Synthetic
mid-write failure rolls back the complete synthetic transaction; receipt rollback
preserves pre-existing/reused edges. No real rollback or automatic write retry occurred.
[Full policy/runbook](MENTIONS_ENRICHMENT.md).

## Tests, lint and Make

| Actual command | Result |
|---|---|
| `make test` | **358 passed, 0 failed**, one upstream TestClient deprecation warning; 79.45 s on final source run |
| Full application coverage | **94.61%** (2,355 statements, 127 missed); XML stays ignored |
| `make unit` | **303 passed, 55 integration cases deselected**, one warning; 18.40 s |
| Unit/API application coverage | **75.84%**, above the CI 60% gate |
| `make lint` | **9.54/10**, all `app` and `scripts`; professor template adapted, no major modules excluded |
| `make format` | Black executed; final source formatting checked through the target |
| `make venv` / `make install` | Container Python 3.12 virtualenv created; locked installation executed; repeat preserves existing environment |
| `make help`, `tree`, `clean` | Executed; clean removes only known source/test caches, never data or credentials |
| `make docker-build` | Both pinned API and Neo4j/GDS images built successfully |
| `make docker-run`, `run`, `health`, `status`, `stats`, `models-check` | Invoked; final live/ready 200, three healthy services, pinned models verified |
| `git diff --check` | Passed |

The first new full test run exposed seven missing-CSV errors because Compose's corpus
volume hid the test checkout's data directory. The read-only test data mount corrected
that, without changing labels. A real topic-query test caught a canonical-name field
mismatch; it was corrected. The first Make formatter used system-container Python
instead of `.venv` Python; the runner was corrected. Startup health was initially
queried before Uvicorn bound its port; bounded Compose `--wait` corrected that race.
All earlier logs remain private instead of being presented as passing runs.

The `.pylintrc` retains the professor's warning policies; visible complexity/style
warnings remain. The exact original professor template and requirements are untouched.
`quality.yml` defines real lint and unit/API coverage jobs with pinned Python/lock.
**No remote workflow has executed these uncommitted changes.** Live integration tests
need local Neo4j/GDS/Ollama and the prepared reviewed corpus and are explicitly separate.

## Live API and agent evidence

Swagger and all new/advanced read endpoints returned HTTP 200. Configured import auth
returned 401 for missing credentials, 403 for wrong credentials and 200/ALREADY_PRESENT
for the correct local token, with an unchanged graph fingerprint. Unconfigured auth
fails closed with 503 in tests. No fresh real corpus import was rerun; the underlying
CLI is exercised through existing synthetic/source tests. The new API corpus volume's
owner was corrected to UID 10001; a real write-access check now passes. No DB volume
ownership was changed.

| Request | Actual result | Wall seconds | Genuine trace |
|---|---|---:|---|
| Q01, DPR encoders/similarity | ANSWERED, exact page-3 source excerpts | 51.618 | catalog → search → source read → source read |
| Q04, Leiden/hierarchy | ANSWERED, exact page-5 excerpts | 53.366 | catalog → search → source read → source read |
| Q08, final corrected run | ANSWERED, two reviewed bibliography excerpts and real path | 54.939 | catalog → directed path → three distinct source reads |
| Q14, final corrected run | REJECTED, no graph query | 0.021 | input guard only |

Q08's actual path arguments were `source_id=arxiv:2404.16130v1`,
`target_id=arxiv:2004.04906v1`, `max_hops=3`. Final answer quotations:
“Retrieval-augmented generation for knowledge-intensive nlp tasks” (GraphRAG p.13)
and “Dense passage retrieval for open-domain question answering” (RAG p.13).
Complete context, source hashes and both approved work-level edges remain in `paths`.
The source text itself remains SOURCE_LOCATED; no new SOURCE_VERIFIED status is granted.

The initial Q08 run repeatedly selected the successful path six times and abstained.
The correction constrains the next choices to every unread path-support Chunk and
stops after all are read. An intermediate answer chose the longest context segment;
final code explicitly selects `support_role=excerpt` and the regression test requires
that choice. Both intermediate traces remain saved. Qwen still directs tool choices
inside the same StateGraph. No expected scientific answer or path is hardcoded.

Q01/Q04 selected statements are their exact quotes; punctuation/caption and partial
sentence residue is retained from parsed source text. Relevance/completeness requires
student semantic review; no new manual evaluation score is asserted. Q15 page-999,
unsafe mutation, invalid selections, quote/hash, duplicate search and tool-budget
controls pass automated regression tests. CPU inference remains slow.

## GDS and optimization

The real validated in-memory projection has three nodes, one logical Jaccard edge
(weight .75), two projected directions and isolated GraphRAG. It used 4,919,960 bytes
at the recorded catalog check. PageRank stream: DPR and RAG each .9999994773,
GraphRAG .15. Louvain groups DPR/RAG and leaves GraphRAG separate; numeric community
IDs are arbitrary. Notebook observed end-to-end algorithm requests of 227.123 ms
(PageRank) and 216.587 ms (Louvain), including evidence validation.

Thirty alternating timed samples after five warmups per query gave baseline/optimized
p50 **1.580/1.148 ms**, p95 **1.895/1.530 ms**. PROFILE DB hits were **2,387/281**, with
identical output; path/shared-dataset plans recorded 118/213 hits. All queries reported
no persisted updates. Tiny warm-cache results do not establish scale or robust clusters.

## ML, notebook, images and resources

The actual frozen pilot used Python 3.12.13/scikit-learn 1.7.2, ten training/five test
Chunks and eight graph features. Logistic accuracy/macro-F1 **0/0**; majority **.6/.375**.
Fit/predict times were .001060/.000241 s versus .000395/.000041 s. [GRAPH_ML.md](GRAPH_ML.md)
contains supports, matrices, distributions and limitations. No post-result tuning or
scientific graph mutation occurred. Original eight-paper/96-label goals remain unmet.

All 18 notebook cells executed on live services. The notebook verifies its initial
and final persisted graph fingerprints agree. Editable draw.io and SVG diagrams are
included; genuine Chromium Swagger/health screenshots were captured and inspected.
The temporary browser install is not in project dependencies or the API image.

A real resource snapshot recorded API **100.4 MiB / 1 GiB**, Neo4j **1.769 GiB / 4 GiB**,
Ollama **4.266 GiB / 6 GiB**. This is a snapshot, not a measured peak. CPU-only inference
and container memory caps are preserved; no GPU acceleration is claimed. Public-image
checks found no `.env`, gold or ML annotation CSV inside the running image. Known local
password/token values were checked against candidate publication files: zero matches.

## Git/review and delivery limits

Git history has 10 Fabrice commits and 19 across Neel's two name variants, including
merge commits. GitHub confirmed merged implementation PR #4 and Fabrice's #5/#8.
PR #4 has substantive code-review threads from Fabrice; PR #5 has Neel's review comments.
The inspected PR #9 returned no comments, and not every PR is proven to meet the
professor's two-constructive-comments condition. Counts do not prove balanced effort.
The final packages are coordinated AI-assisted preparation, not fabricated independent
teammate authorship or review.

The external handoff manifests list exact file hashes, patch hashes, base commit,
application order and actual temporary-worktree validation. Package A owns core code,
tests, configuration and implementation records; Package B owns README, notebook,
diagrams, screenshots, demonstration guide and final rubric. Paths are disjoint.
Operator publication, commits/PRs/merges, remote CI, final human review, public API image
publication and any academic submission remain outstanding. No private backup, PDF,
credential, full export or trained model is carried by either patch.
