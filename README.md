# GraphDBproject-NeelSabharwal-FabriceAfopa

AI Research GraphRAG Assistant — academic Project 8, Level 3+.

The current implementation includes local infrastructure and three-paper evidence ingestion: Neo4j Community with GDS, a health-only FastAPI backend, CPU-only Ollama, and a provenance-aware ingestion CLI. The LangGraph agent, graph analytics and ML remain future work. Deadline: Friday, October 23, 2026. Two students; user is team lead. Budget: zero paid APIs, cloud services or subscriptions.

See [local setup, version/license notes and actual verification evidence](docs/INFRASTRUCTURE.md). Docker/Compose, Python 3 for setup scripts and GNU Make are required on the host. System Python is not replaced; the backend uses Python 3.12 in Docker.

```bash
make configure
make docker-build
make docker-run
make models-pull
make health
make test
make smoke
```

Open Swagger at <http://localhost:8000/docs>. Readiness returns 503 until Neo4j/GDS and both required model tags are available. Only API port 8000 is published, on localhost. Downloaded models persist in a Docker named volume; credentials remain in ignored `.env`. `make help` lists the implemented commands; `make docker-stop` preserves data volumes.

On the assessed WSL environment Make was absent; a temporary local Make executable was used for verification. See the setup guide for this limitation and the normal installation remedy. Full project documentation, screenshots, CI badges and registry publication remain outstanding; no image has been published.

Planning references: [brief](PROJECT_BRIEF.md), [milestones and grading map](PROJECT_PLAN.md), [architecture](docs/ARCHITECTURE.md), [decisions](docs/DECISIONS.md), and [professor requirements](docs/requirements/projects_spec.md).

Three-paper ingestion: after rebuilding the API image for its pinned pypdf dependency,
run `make ingest`. It verifies the three prototype PDFs from the
[research manifest](corpus/corpus_manifest.json), imports page-bounded chunks and
validated bibliography evidence, and runs one bounded local extraction per paper.
`make test` runs the current checkout in a temporary container and writes coverage to
ignored `data/processed/coverage.xml`. See [ingestion policy, commands and measured
results](docs/INGESTION.md). Research source files are preserved; generated PDFs,
full text, raw model responses and audit reports remain under ignored `data/`.
