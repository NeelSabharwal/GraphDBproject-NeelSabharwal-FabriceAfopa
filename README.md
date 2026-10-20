# GraphDBproject-NeelSabharwal-FabriceAfopa

AI Research GraphRAG Assistant — academic Project 8, Level 3+.

The current implementation includes local infrastructure, three-paper evidence ingestion,
Neo4j vector retrieval and a bounded LangGraph agent at `/api/ask`, using CPU-only Ollama.
Graph analytics and ML remain future work. Deadline: Friday, October 23, 2026.
Two students; user is team lead. Budget: zero paid APIs, cloud services or subscriptions.

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

After importing the corpus and rebuilding the API, run `make embed` to prepare or reuse
the pinned chunk embeddings and cosine index. Then use Swagger or:

```bash
curl --get --data-urlencode 'q=How does DPR encode questions and passages?' \
  http://localhost:8000/api/ask
```

The response contains checked source citations, operational tool traces and explicit
limitations. Generated interpretations are hypotheses; citation/scientific graph
traversal requires actual student approval. CPU inference can take tens of seconds or
abstain. See [agent configuration, reproduction and measured results](docs/AGENT.md).
Health checks establish dependency availability, not vector readiness or answer quality.

Agent limits are documented in `.env.example` and validated at startup. Paper-specific
search ranks eligible embeddings within a 256-chunk bound; larger papers fail explicitly.
Scientific expansion excludes the starting paper and requires approved claims on both sides.
`make test` tests current working-tree files using the running API's dependencies.
Rebuild the API after dependency changes. A passing dirty-tree run does not verify a
Git commit: include all integration files, then rebuild/test the eventual pushed revision.
