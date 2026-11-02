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

## Rubric gap closure follow-up — 2026-11-02

This section supersedes the earlier *publication/remote-CI status*, not the historical
local execution record. PR #10 merged as `b85e035d27ed6898aa035f40d5fdb4d6d5e280a6`;
PR #11 merged as `f46b2a9757522ea7809e8e02df6d5431729e8727`. The isolated worktree
`/tmp/project8-final-rubric-completion` on `feat/final-rubric-completion` starts at the
latter `origin/main`. The original `feat/final-core-ml` checkout's modified README,
10-file documentation package and `.vscode/settings.json` were preserved. WSL had no
Git credentials; the existing authenticated Windows GitHub CLI was used for a single
fetch without persisting credential changes. No commit/push/merge or image publication
was performed in this follow-up.

### Actual remote CI

GitHub API job results and logs were inspected, not inferred from workflow YAML.
Every listed run completed successfully, with both `lint` and `unit-api` successful:

| Revision / event | Actual GitHub run |
|---|---|
| PR #10 head `873ef25`, push | [41469574427](https://github.com/NeelSabharwal/GraphDBproject-NeelSabharwal-FabriceAfopa/actions/runs/41469574427) |
| PR #10 head `873ef25`, pull request | [41469794934](https://github.com/NeelSabharwal/GraphDBproject-NeelSabharwal-FabriceAfopa/actions/runs/41469794934) |
| PR #10 merge `b85e035`, main push | [41470070441](https://github.com/NeelSabharwal/GraphDBproject-NeelSabharwal-FabriceAfopa/actions/runs/41470070441) |
| PR #11 head `a2f73d4`, pull request | [41478861875](https://github.com/NeelSabharwal/GraphDBproject-NeelSabharwal-FabriceAfopa/actions/runs/41478861875) |
| PR #11 head `a2f73d4`, push | [41479013723](https://github.com/NeelSabharwal/GraphDBproject-NeelSabharwal-FabriceAfopa/actions/runs/41479013723) |
| PR #11 merge `f46b2a9`, main push | [41480888111](https://github.com/NeelSabharwal/GraphDBproject-NeelSabharwal-FabriceAfopa/actions/runs/41480888111) |

The last run's [lint log](https://github.com/NeelSabharwal/GraphDBproject-NeelSabharwal-FabriceAfopa/actions/runs/41480888111/job/125398556803)
reports **9.54/10**. Its [unit/API log](https://github.com/NeelSabharwal/GraphDBproject-NeelSabharwal-FabriceAfopa/actions/runs/41480888111/job/125398557775)
reports **303 passed, 55 deselected, one warning, 17.51 s; 75.84% coverage**.
The unchanged workflow uses Python 3.12.13, the dependency lock, the 9.5 lint gate and
60% unit/API coverage gate. Live integration tests deliberately remain local. These
runs verify merged main, not this uncommitted follow-up. README's workflow badge now
explicitly follows main; its build and coverage badges identify their measured scope
and date/revision. Private-repository CI links require access; anonymous badge failure
must not be mistaken for failed tests.

### Scoped changes and fresh local checks

Added **52 useful public class/function docstrings in 11 files**. Module and public
interface AST inspection finds no missing docstrings. Pylint's three missing-docstring
checks are now enabled, with no missing-docstring findings. Removing docstrings from
both ASTs proves all changed Python executable structures equal their merged-main
versions; no graph query, label, model parameter or scientific review changed.

| Command/check in the isolated worktree | Actual outcome |
|---|---|
| `make format` | Black completed; four files reformatted, 65 unchanged |
| `make lint` | **9.54/10**, exit 0, all app/scripts, missing-docstring checks enabled |
| `make test` (corrected read-only data mounts) | **358 passed, zero failures**, one upstream warning, **35.01 s** |
| Full suite coverage | **94.61%**, 2,355 statements / 127 missed |
| `make unit` | **303 passed, 55 deselected**, one warning, **9.66 s**, **75.84% coverage** |
| `make help tree clean health status models-check` | Exit 0; both health requests 200, all three services healthy, both pinned model digests match |
| API-only `docker build` | Completed locally; no push, no running service replacement |
| Offline final-image smoke | `/health/live`, `/docs`, `/openapi.json` each 200; both supplemental license notices present |
| Source/annotation protection | Requirements, corpus/review inputs, ML CSV, gold and student review documents unchanged |
| Git hygiene | `git diff --check` passes; no staged files; private-path ignore probes pass |

Test commands used existing pinned Docker Python/.venv and healthy dependencies,
mounting this worktree as source, its tracked data read-only, original PDFs read-only,
and only ignored output paths writable. The first test invocation omitted the tracked
data mount; the API corpus volume hid `data/ml/chunk_label_candidates.csv`, producing
**7 failed / 351 passed**. Correcting only the temporary runner mount yielded the
successful full run above. Both logs are retained under ignored
`data/processed/rubric-completion/`; no CSV repair or label substitution was made.
Startup/build/install Make target definitions are unchanged from the earlier actually
executed record; they were inspected with `make -n` here. This task did not restart the
live stack or reinstall its environment merely to repeat unchanged startup evidence.
Notebook dependencies are explicitly documented; the prior successful 18-cell run is
retained and is not misrepresented as a fresh notebook execution.

Before/after read-only snapshots have identical full fingerprint
`0a17d318be0066b5b7fb20a88e1821586cc3135c07dbbd9a27012ebfe363d62f`:
3 Papers, 153 Chunks, 17 Entities, 25 Claims (22 approved / 3 pending), 148 MENTIONS,
2 CITES, 60 SUPPORTED_BY; all 153 embeddings remain. The full suite exercises and
cleans synthetic transactional fixtures; it did not reimport the corpus, repeat the
145-edge enrichment, approve claims or rerun the frozen real ML experiment.

### API image readiness

Final local image ID (not a published registry digest):
`sha256:dd2db095d68a56e03ea71dbbc72270ac29d0d20dac80984f04df1b8d739d76c3`,
794,328,354 bytes, non-root `appuser`. The pinned base and dependency lock are unchanged.
The image gains its repository-source label and two upstream notices missing from
installed wheels; 94 installed Python distributions were inventoried. No license is
invented for the students' code. [Publication guide](IMAGE_PUBLICATION.md) documents
sources, permissions, exact GHCR commands and the private-source disclosure gate.

The offline filesystem audit inspected 24,763 file paths, including 76 workspace
files: no forbidden private project paths or configured credential values were found.
The byte scan covers workspace/home/root files below 10 MB; it is not an exhaustive
base-image vulnerability or historical-layer secret scan. Docker build inputs were
also reviewed: no secret ARG/COPY or private data path exists. A tracked/nonignored
source scan and representative ignore checks passed; Git history showed no committed
`.env`, PDF, model-weight, key, raw or processed-data paths in the checked patterns.
No Neo4j/GDS image, model or PDF is included or published. R04 stays MISSING until a
separately authorized push, public visibility, anonymous pull and real README digest/link.

### Actual collaboration record

At merged main `f46b2a9`, `git shortlog -sn HEAD` reports 11 commits under each of
`NeelSabharwal`, `Neel Sabharwal`, and `Fabrice Afopa`: **Neel 22/33 (66.7%)**, Fabrice
11/33 (33.3%), including merges. Excluding merges: **11 each (50%/50%)**. These are
history counts, not measured effort or proof of independent work. PR #10 is Neel's
core integration; PR #11 is Fabrice's documentation integration. AI-assisted package
preparation remains disclosed. R47 remains PARTIAL pending substantive assessment.

All PRs #1–#11 were queried for discussion, inline and review records. Nonempty content
was inspected separately from empty review-submission records:

| PR | Observed substantive review evidence | Limit |
|---|---|---|
| [#1](https://github.com/NeelSabharwal/GraphDBproject-NeelSabharwal-FabriceAfopa/pull/1) | Fabrice: dependency-failure health test and malformed Ollama payload handling; Neel replies with fixes | Historical comments are not new independent test runs |
| [#2](https://github.com/NeelSabharwal/GraphDBproject-NeelSabharwal-FabriceAfopa/pull/2) | Fabrice: entity/Chunk consistency, citation failure handling, atomic PDF saving; Neel replies | Three concrete review concerns preserved |
| [#3](https://github.com/NeelSabharwal/GraphDBproject-NeelSabharwal-FabriceAfopa/pull/3) | Neel: reproducible evidence verifier and page-999 fixture separation; Fabrice replies | Evaluation review distinct from gold/application success |
| [#4](https://github.com/NeelSabharwal/GraphDBproject-NeelSabharwal-FabriceAfopa/pull/4) | Fabrice: router wiring, self-match exclusion, bounded paper retrieval; later inspection replies | Formal state COMMENTED, not invented APPROVED; independent run explicitly pending |
| [#5](https://github.com/NeelSabharwal/GraphDBproject-NeelSabharwal-FabriceAfopa/pull/5) | Neel's requested scientific/alias checks and later documentation-integration review | Two nonempty records; formal review COMMENTED |
| [#6](https://github.com/NeelSabharwal/GraphDBproject-NeelSabharwal-FabriceAfopa/pull/6) | No returned discussion/inline/review records; not merged | No review credit inferred |
| [#7](https://github.com/NeelSabharwal/GraphDBproject-NeelSabharwal-FabriceAfopa/pull/7) | No returned discussion/inline/review records | Merged does not establish review |
| [#8](https://github.com/NeelSabharwal/GraphDBproject-NeelSabharwal-FabriceAfopa/pull/8) | Neel's actual 15 whole-Chunk approval comment | One record; scientific label approval is not two code-review comments |
| [#9](https://github.com/NeelSabharwal/GraphDBproject-NeelSabharwal-FabriceAfopa/pull/9), [#10](https://github.com/NeelSabharwal/GraphDBproject-NeelSabharwal-FabriceAfopa/pull/10), [#11](https://github.com/NeelSabharwal/GraphDBproject-NeelSabharwal-FabriceAfopa/pull/11) | No returned discussion/inline/review records | R42 remains PARTIAL |

No comments, approvals, author identities or retrospective review timestamps were
created. Students can conduct genuine follow-up reviews and document their real dates;
these cannot establish that pre-merge reviews occurred when they did not.

## Final acceptance — 2026-11-02

Isolated worktree `/tmp/project8-final-acceptance`, branch `feat/final-acceptance`,
base `b782bbfcfcbebf6ae3a66074a1502036a3428a66` (merged PR #12). PRs #10/#11/#12
are all ancestors. The original `feat/final-core-ml` checkout and its locally edited
and untracked teammate files were preserved. Cleanup preceded this build/test run;
see [REPOSITORY_CLEANUP.md](REPOSITORY_CLEANUP.md). No file/dependency was deleted or
renamed. One unused import was removed, historical/current navigation clarified,
and two notebook visualizations added using existing dependencies.

### Actual fresh local checks

| Command/check | Observed result |
|---|---|
| `make format` | Black passed; existing Python formatting retained |
| `make docker-build` | API and local-only Neo4j/GDS builds completed; neither published |
| `make docker-run` | Three services healthy using existing named volumes |
| `make health` | live 200 / ready 200; Neo4j/GDS and Ollama checks both ok |
| `make models-check` | Both installed model digests match models.lock.json |
| `make lint` | **9.55/10** on app and scripts; minimum 9.5 passed |
| `make unit` | **303 passed, 55 deselected**, one warning, 10.46 s; **75.84%** coverage |
| `make test` | **358 passed**, zero failures, one warning, 44.61 s; **94.61%** coverage |
| `make notebook` | **22 cells executed**, all 11 code cells have execution counts; no cell errors; two actual SVG outputs |
| `make help tree clean status stats` | All completed; clean removes only documented caches; data preserved |
| Git/document checks | Diff whitespace, 49 exact rubric rows/100 points, local Markdown file links, output-free notebook and protected-file hashes checked |

These Make commands used an operational wrapper in `/tmp`: `COMPOSE_ENV_FILES` points
to the existing ignored `.env`; PYRUN mounts the acceptance source/data read-only,
the existing pinned Python 3.12 `.venv` read-only, raw PDFs and original ML artifacts
read-only, and only acceptance `data/processed` writable. No credentials were copied
into tracked files or printed. The source lock/Makefile are unchanged. Historical
`venv`, `install` and `run` checks above remain evidence; dependencies were not
reinstalled into the original checkout for this documentation/notebook change.
Full/unit coverage files are separate; each test container has its own `/tmp/.coverage`.
The warning is upstream TestClient deprecation. Notebook warnings concerned an
unwritable IPython home falling back to `/tmp`; execution succeeded.

### Graph, agent, security and frozen experiment

Before and after tests and notebook, the persisted graph fingerprint is:
`0a17d318be0066b5b7fb20a88e1821586cc3135c07dbbd9a27012ebfe363d62f`.
Actual state: **3 Papers, 153 Chunks, 17 Entities, 25 Claims (22 SOURCE_VERIFIED /
3 EXTRACTED), 2 CITES, 148 MENTIONS and 153 embeddings**. Other relationships:
153 PART_OF, 150 NEXT, 25 SUBJECT, 25 OBJECT, 60 SUPPORTED_BY. All 11 indexes are
ONLINE and four uniqueness constraints exist. Neo4j is 5.26.32; GDS is 2.13.2.

Live Swagger, corpus, concept-neighborhood, directed path, shared-dataset, PageRank
and Louvain requests succeeded. The actual path remains GraphRAG → RAG → DPR; the
four shared DPR/RAG datasets remain Natural Questions, TriviaQA, WebQuestions and
CuratedTREC. GDS streams over three nodes / one logical weight-.75 edge (two stored
projection directions), with GraphRAG isolated. No persisted GDS write or reimport
was performed. Import authentication returned missing 401, wrong 403, configured
200 with **ALREADY_PRESENT**, and a post-request fingerprint comparison passed.
The authenticated request exercised the existing-corpus early return, not fresh ingestion.

The notebook's live Q04 returned ANSWERED/HYPOTHESIS in **44,598.934 ms** with actual
`paper_catalog → search_chunks → get_source_excerpt → get_source_excerpt` trace.
It selected the page-5 Leiden/community figure caption, mechanically source-located;
relevance/completeness remain subject to student assessment, not a new scientific
approval. The unsafe request was REJECTED by `input_guard`. Page-999 forged citation
and other action/budget/quote controls passed in the automated suite; this does not
mean every possible model response is safe or semantically correct.

The frozen ML report was read, not regenerated: logistic accuracy **0**, macro-F1 **0**,
confusion matrix `[[0,2],[3,0]]`; majority accuracy **0.6**, macro-F1 **0.375**,
`[[0,2],[0,3]]`. All 23 protected source/review/requirement/gold/label/model artifact
hashes match the pre-task inventory. No labels, decisions or results were changed.
One post-demo resource snapshot: API 100.6 MiB/1 GiB, Neo4j 1.789 GiB/4 GiB, Ollama
4.269 GiB/6 GiB. This is a snapshot, not measured peak usage.

### Remote CI and collaboration evidence

The prior completion branch is merged. All three associated quality runs succeeded:
[PR #12 push](https://github.com/NeelSabharwal/GraphDBproject-NeelSabharwal-FabriceAfopa/actions/runs/41486094364),
[PR #12 pull-request run](https://github.com/NeelSabharwal/GraphDBproject-NeelSabharwal-FabriceAfopa/actions/runs/41486168603),
and [merged main b782bbf](https://github.com/NeelSabharwal/GraphDBproject-NeelSabharwal-FabriceAfopa/actions/runs/41487540210).
Main [lint job](https://github.com/NeelSabharwal/GraphDBproject-NeelSabharwal-FabriceAfopa/actions/runs/41487540210/job/125421711673)
reported **9.54/10**; main [unit/API job](https://github.com/NeelSabharwal/GraphDBproject-NeelSabharwal-FabriceAfopa/actions/runs/41487540210/job/125421711774)
reported **303 passed / 55 deselected / 75.84% / 17.36 s**. These are actual remote
results, distinct from the new local 9.55/358-test run. Acceptance-branch CI is checked
after push and reported on its PR; a successful main run does not substitute for it.

The previous PR #1–#11 review audit remains valid; #12 adds zero issue/review comments.
At b782bbf, Git records Neel's spelling variants separately (12 `Neel Sabharwal` +
12 `NeelSabharwal`) and 11 Fabrice commits including merges; non-merge totals are
Neel 12 / Fabrice 11. No authorship was rewritten. Counts and actual merged PRs support
participation but cannot establish balanced substantive work or meet the two-comments
rule retroactively. No closed PR metadata was edited for cosmetic uniformity.

### Public image and privacy

The source repository API returned `private: true`, `visibility: private`.
API-only publication authorization is recorded, but publication stopped before any
external upload because the existing OAuth credential lacks package-write scope and
Docker has no registry login. Source/notice verification is also incomplete for all
redistributed compiled components. [IMAGE_PUBLICATION.md](IMAGE_PUBLICATION.md)
records exact blockers and operator steps; no token is requested in chat.

Final local API ID is `sha256:422b77a9635d5b585385c241a39668674827cef0c2959ef0eaee20a46c3e4477`,
linux/amd64, 794,328,467 bytes, appuser UID 10001. All **15 layers** were inspected,
with zero configured-secret, workspace token/private-key signature or forbidden-path
matches. The inventory contains 94 Python distributions and 105 base copyright files;
two missing wheel notices are supplied from pinned upstream sources. No GHCR tag,
package page, registry digest, public visibility or anonymous pull is claimed. The
custom Neo4j/GDS image remains local. This is not a complete vulnerability audit.

Private logs/inventories/image archive/executed notebook remain ignored under
`data/processed/`. No such artifacts are part of the acceptance commit. Final remaining
human steps are genuine reviews, publication gate resolution, contribution assessment,
oral defense and academic submission/late-delivery acceptance. No 100/100 grade is claimed.
