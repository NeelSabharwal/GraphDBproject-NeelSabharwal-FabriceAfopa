# Local infrastructure foundation

Scope: three local services, health endpoints, pinned software, real model and Bolt/GDS smoke checks. No paper ingestion, application graph, LangGraph agent, GDS analytics or ML is implemented by this milestone. Deadline is Friday, October 23, 2026; two students, user is team lead; budget is strictly zero paid services.

## Reproduce locally

Prerequisites: running Docker Desktop with Ubuntu WSL integration, Docker Compose, Python 3 for host setup scripts, and GNU Make. The API itself uses Python 3.12.13 in Docker; WSL's Python 3.14.4 is not replaced. This local development image includes pytest so tests do not require a host virtual environment.

```bash
make configure
make docker-build
make docker-run
make models-pull
make health
make models-check
make test
make smoke
make status
make stats
```

`configure` creates a random password in ignored `.env`, mode 0600; it preserves existing files. `.env.example` contains a placeholder only. Do not print `.env`, unredacted `docker compose config`, container environment dumps or authentication arguments in reports. If supplying your own password, use a random string of at least 16 characters. Changing `.env` does not rotate an existing Neo4j volume's password automatically.

The first `docker-run` starts services before models are downloaded; API readiness intentionally returns 503 with `models_missing` until `models-pull` completes. Ollama's own health check tests its server, not loaded model quality. Model tags are mutable: `models-check` compares installed manifest digests with `models.lock.json`; a mismatch fails rather than silently updating the lock. Downloads require internet but local inference needs no hosted API or paid account. `make smoke` makes real inference requests and may take time on CPU.

Swagger: <http://localhost:8000/docs>. Health: `/health/live` and `/health/ready`. Only localhost port 8000 is published. Bolt 7687, Neo4j HTTP 7474 and Ollama 11434 stay inside the Compose network. Use `docker compose exec -T api ...` for internal checks. `make docker-stop` preserves named volumes; deleting volumes would delete graph/model data and is not part of this procedure.

WSL had no `make` command during implementation; `sudo -n apt-get install make` could not authenticate. For this session, the official Ubuntu `make_4.4.1-3_amd64.deb` was downloaded and extracted under `/tmp/graphrag-make/extracted`, without changing system packages. Commands were executed with `/tmp/graphrag-make/extracted/usr/bin/make TARGET`. That temporary location may disappear; the normal remedy is for the student to run `sudo apt-get install make` once, or extract the Ubuntu package into another user-owned tools directory and add its `usr/bin` to PATH. No administrator password was requested, stored or bypassed.

## Version, source and license records

| Component | Pin/source | License/use note |
| --- | --- | --- |
| Neo4j | `5.26.32-community`, image digest in `docker/neo4j.Dockerfile` | Community GPLv3; no Enterprise DB image/key |
| GDS | `2.13.2`, [official release](https://github.com/neo4j/graph-data-science/releases/tag/2.13.2), SHA-256 `edb7ce2ae1642449073ed2fd72b8438ce312fefee0b3ae04dbb0854eaecbd16f` | Community runtime without Enterprise license key; see packaging note below |
| Python | `3.12.13-slim-bookworm`, image digest in Dockerfile | Isolated from system Python |
| Python packages | Exact runtime/test/transitive versions in `requirements.lock.txt` | Runtime direct dependencies also listed in `requirements.txt` |
| Ollama | `0.40.6`, official image digest in Compose | Local CPU backend; cloud disabled; no GPU devices passed |
| Qwen | `qwen2.5:3b-instruct`, Q4_K_M, advertised about 1.9 GB before download | [Qwen Research License](https://ollama.com/library/qwen2.5:3b-instruct/blobs/b5c0e5cf74cf), non-commercial research/evaluation; not Apache 2.0 |
| Nomic | `nomic-embed-text:v1.5`, advertised about 274 MB before download | [Apache 2.0 model card](https://huggingface.co/nomic-ai/nomic-embed-text-v1.5); embeddings only; use `search_query:`/`search_document:` prefixes |

The [compatibility matrix](https://neo4j.com/docs/graph-data-science/current/installation/supported-neo4j-versions/) pairs Neo4j 5.26 with GDS 2.13; the 2.13.2 release specifically fixes Community Edition compatibility. The plugin is baked into the image with a verified checksum, never selected by a runtime `latest` plugin installer.

GDS packaging note: upstream OpenGDS source is GPLv3, but this official release JAR also bundles a `LICENSE.txt` headed “NEO4J, INC. PRE-RELEASE AGREEMENT” and Enterprise classes. Do not label the whole binary simply GPL or assume redistribution rights from the source license. Official [edition documentation](https://neo4j.com/docs/graph-data-science/current/introduction/#editions) states the plugin defaults to Community and an Enterprise key unlocks additional features; this setup supplies no key. Inspect `gds.isLicensed()` in the smoke report. No image/plugin redistribution is performed; clarify bundled binary terms before any future registry publication of the custom Neo4j image. Publishing a clean API image is a separate future task.

## Resource and readiness boundaries

The observed WSL/Docker ceiling is 15.30 GiB with 16 logical CPUs; swap is 4 GiB. Compose sets memory limits of Neo4j **4 GiB**, Ollama **6 GiB**, API **1 GiB**: **11 GiB total**, leaving about 4.3 GiB outside these containers. Memory-plus-swap limits equal RAM limits, so containers cannot consume extra swap. CPU quotas are 3/8/2. Neo4j heap is 1 GiB and page cache 512 MiB; unused headroom covers native/plugin needs. This is a starter allocation, not proof of future corpus/GDS sizing.

Ollama allows one resident model and one request at a time. Default context is 2048; smoke requests explicitly select CPU (`num_gpu=0`), eight threads, temperature 0 and seed 42. The model-smoke report includes `/api/ps` memory/offload fields. Intel acceleration is not configured or investigated.

Readiness concurrently checks authenticated Bolt plus exact GDS 2.13.2, and Ollama's required model tags. Each probe has a 3-second outer deadline; failed probes yield safe 503 responses without raw exceptions. Liveness is independent. Health calls never perform inference, create projections, mutate the graph or download anything. Future schema/vector-index readiness is deferred because those features do not yet exist.

## Verification evidence

The actual smoke command writes `data/processed/infrastructure-smoke.json` (ignored) with model outputs, digests/sizes, request timings, versions, HTTP status, GDS procedures and container cgroup memory measurements. `memory.peak` is the kernel peak since container creation and includes charged cache; it is not a per-request peak or the same metric as Docker's cache-adjusted display. Coverage XML is generated inside the API container at `/tmp/coverage.xml`; no score is implied before running tests.

The structured-output smoke validates the real response against Pydantic and checks expected values. The tool smoke validates a real returned tool name and arguments; it does not implement an agent or execute a paper lookup. Embeddings are checked for 768 finite dimensions and a nonzero norm. The Bolt smoke authenticates, reads exact database/GDS versions, inspects procedure registration and actually invokes `gds.graph.list()`. It does not run PageRank/Louvain or satisfy the two-algorithm criterion.

### Actual run — 2026-10-19, approximately 18:51 Europe/Paris

`make smoke` exited 0; all four model cases passed. This is one small smoke run, not a latency benchmark or extraction-quality evaluation.

| Case | Actual wall time | Observed result |
| --- | ---: | --- |
| Basic text, first generation/model load | 5.012 s | `Yes, I can answer locally.`; reported model load 4.306 s |
| Structured JSON, warm generation | 1.054 s | Pydantic-valid `{"project":"GraphRAG","local_only":true}` with expected values |
| Tool request, warm generation | 2.613 s | One actual `lookup_paper` call with `{"paper_id":"2005.11401"}`; no tool executed or agent implemented |
| Embedding, switched model | 0.591 s | One finite 768-dimensional vector; L2 norm 1.0; reported load 0.561 s |

Runtime versions: **Python 3.12.13**, **FastAPI 0.115.12**, Neo4j **5.26.32 Community**, GDS **2.13.2**, Ollama **0.40.6**. Authenticated Bolt/GDS smoke took 0.222 s. `gds.isLicensed()` returned **false** (no Enterprise key). `gds.graph.list`, `gds.graph.project`, `gds.pageRank.stream` and `gds.louvain.stream` were registered; `gds.graph.list()` actually executed and returned an empty catalog. No projection or algorithm was run.

Installed model metadata is preserved in `models.lock.json`: Qwen **1,929,912,432 bytes**, manifest `357c53fb659c5076de1d65ccb0b397446227b71a42be9d1603d46168015c9e4b`; Nomic **274,302,450 bytes**, manifest `0a109f422b47e3a30ba2b10eca18548e944e8a23073ee3f3e947efcf3c45e59f`. Combined manifest sizes are about 2.20 GB decimal, not a promise about complete Docker disk use. `/api/ps` reported `size_vram=0` for both models and a 2048-token context. No Intel GPU acceleration was attempted.

| Container | Kernel memory peak since creation | Configured cap | OOM / OOM-kill events |
| --- | ---: | ---: | --- |
| Neo4j | 2.073 GiB | 4 GiB | 0 / 0 |
| API | 0.142 GiB | 1 GiB | 0 / 0 |
| Ollama | 4.104 GiB | 6 GiB | 0 / 0 |

These peaks include cache and may occur at different times; do not sum them as a measured simultaneous peak. A later Docker stats snapshot showed approximately 1.633 GiB Neo4j, 70.1 MiB API and 1.942 GiB Ollama. WSL reported about 11 GiB available RAM after the run and 1.3 MiB of its 4 GiB swap in use. Container swap remained disabled; the WSL snapshot includes other processes and filesystem caches.

### Commands and actual verification results

All `make` invocations below used the temporary GNU Make 4.4.1 executable described above; an unqualified host `make` still requires installation/PATH setup.

- `docker compose config --quiet`: exit 0; subsequent credential-safe JSON inspection confirmed three services, 11 GiB total limits, equal RAM/memory-plus-swap caps, health checks and only a localhost API binding. The initial inspection helper assumed numeric JSON fields and raised TypeError; conversion of Compose's string byte counts fixed the helper, and the audit passed without changing configuration.
- `make configure`: setup script first created mode-0600 ignored `.env`; its value was never displayed. A later actual Make invocation preserved the existing file, verified byte-for-byte by hash comparison.
- `make help`, `make docker-build`, `make docker-run`: executed successfully through the local Make binary. The first direct `make docker-build` attempt failed because Make was absent; direct Compose build and the local Make remedy succeeded.
- `docker compose exec -T ollama ollama pull qwen2.5:3b-instruct` and the corresponding `nomic-embed-text:v1.5` command: completed successfully. `make models-check`: both full manifest digests matched the lock.
- Before model installation, actual API responses were live **200**, ready **503** with `models_missing`, docs **200**. After installation, `make health` returned live **200** and ready **200** with both dependency checks `ok`. Smoke also fetched `/docs` and `/openapi.json`, both **200**.
- Initial isolated health run: **10 passed, 2 integration tests deselected**; separate real Bolt/GDS test: **1 passed**. Early pytest cache-permission warnings were fixed by using `/tmp`; one upstream Starlette/AnyIO BlockingPortal deprecation warning remains.
- Final `make test`: **12 passed, 1 warning in 1.14 s**; **72 statements, 0 missed, 100% coverage** of the current health-only application. No tests skipped/deselected in this full run. XML generated at `/tmp/coverage.xml` and copied to ignored `data/processed/coverage.xml`; this small foundation coverage does not establish coverage of future ingestion/agent code.
- `make smoke`: **exit 0**, actual outputs/timings above; raw JSON saved under ignored `data/processed/`.
- `make status`: **api, neo4j and ollama all running and healthy**. `make stats` produced the observed memory snapshot above. Services were deliberately left running for review; `make docker-stop` is available but was not executed after the smoke run.
- Source parsing and `git diff --check`: passed. Actual generated password absent from project sources/docs/configuration; `.env` ignored; build context excludes credentials and raw data. Both professor documents and AGENTS.md retain their original SHA-256 hashes. No commit, push or image publication occurred.

No model inference or GDS runtime blocker remains in this small test. Remaining limitations are host Make availability, the documented GDS binary redistribution terms, one dependency deprecation warning, and unmeasured performance/quality on realistic research-paper extraction and repeated agent tool use. A successful single tool-selection case does not prove reliable multi-step agent behavior. Next task should review this evidence, assign work between the two students, then approve a small schema/provenance and three-paper parsing/extraction milestone; do not silently begin ingestion.

## File inventory for this milestone

Created source/configuration files:

- `docker-compose.yml`, `Dockerfile`, `docker/neo4j.Dockerfile`, `.dockerignore`, `.env.example`, `Makefile`.
- `requirements.txt`, `requirements-dev.txt`, `requirements.lock.txt`, `pyproject.toml`, `models.lock.json`.
- `app/__init__.py`, `app/config.py`, `app/health.py`, `app/main.py`.
- `scripts/__init__.py`, `scripts/configure.py`, `scripts/check_models.py`, `scripts/smoke.py`, `scripts/verify_infrastructure.py`.
- `tests/test_health.py`, `tests/test_connectivity.py`, `docs/INFRASTRUCTURE.md`.

Updated existing files: `.gitignore`, `README.md`, `PROJECT_BRIEF.md`, `PROJECT_PLAN.md`, `docs/ARCHITECTURE.md`, `docs/DECISIONS.md`. Existing planning content was retained with dated scope/evidence updates. Both professor documents and `AGENTS.md` were preserved.

Created local ignored artifacts: `.env`, `data/processed/infrastructure-smoke.json`, `data/processed/coverage.xml`. Docker named volumes hold database/log/model files outside the repository. Download/build console logs and the temporary Make executable are under `/tmp`, not repository source. Nothing was staged, committed, pushed or published.
