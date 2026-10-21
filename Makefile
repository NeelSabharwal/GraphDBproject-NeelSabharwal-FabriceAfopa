.PHONY: help configure docker-build docker-run status health models-pull models-check test smoke stats docker-stop ingest embed

help:
	@printf '%s\n' 'configure     Generate ignored local .env (preserves existing file)' 'docker-build  Build pinned API and Neo4j/GDS images' 'docker-run    Start the three local services (pull models separately)' 'models-pull   Download approved model tags, then verify manifest digests' 'models-check  Compare installed models with models.lock.json' 'status        Show Compose service status' 'health        Check live/ready; fails if dependencies/models unavailable' 'stats         Show one container resource snapshot' 'test          Run unit and real-dependency tests with coverage in API container' 'smoke         Run actual CPU inference/JSON/tool/embedding and Bolt/GDS smoke tests' 'docker-stop   Stop this stack without removing data volumes'
	@printf '%s\n' 'ingest        Verify/import three prototype PDFs; one cached Ollama sample per paper'
	@printf '%s\n' 'embed         Create/reuse pinned Chunk embeddings and verify the vector index'

embed:
	docker compose exec -T api python -m scripts.embed_chunks

configure:
	python3 scripts/configure.py

docker-build:
	docker compose build

docker-run:
	docker compose up -d --build

status:
	docker compose ps

health:
	docker compose exec -T api python -c "import httpx; c=httpx.Client(base_url='http://127.0.0.1:8000',timeout=5); a=c.get('/health/live'); b=c.get('/health/ready'); print(a.status_code,a.json()); print(b.status_code,b.json()); a.raise_for_status(); b.raise_for_status()"

models-pull:
	docker compose exec -T ollama ollama pull qwen2.5:3b-instruct
	docker compose exec -T ollama ollama pull nomic-embed-text:v1.5
	python3 scripts/check_models.py

models-check:
	python3 scripts/check_models.py

test:
	@mkdir -p data/processed
	@set -eu; \
		test_workspace=$$(docker compose exec -T api mktemp -d /tmp/graphrag-tests.XXXXXX); \
		trap 'docker compose exec -T -u 0 api rm -rf "$$test_workspace"' EXIT; \
		for item in app scripts tests pyproject.toml; do \
			docker compose cp "$$item" "api:$$test_workspace/"; \
		done; \
		result=0; \
		docker compose exec -T -w "$$test_workspace" api python -m pytest \
			--cov=app --cov-report=term-missing --cov-report=xml:coverage.xml || result=$$?; \
		docker compose cp "api:$$test_workspace/coverage.xml" data/processed/coverage.xml; \
		exit $$result

ingest:
	@mkdir -p data/raw data/processed
	docker compose run --rm --no-deps --user "$$(id -u):$$(id -g)" \
		-v "$(CURDIR)/app:/workspace/app:ro" -v "$(CURDIR)/scripts:/workspace/scripts:ro" \
		-v "$(CURDIR)/corpus:/workspace/corpus:ro" -v "$(CURDIR)/models.lock.json:/workspace/models.lock.json:ro" \
		-v "$(CURDIR)/data:/workspace/data" api python -m scripts.ingest

smoke:
	python3 scripts/verify_infrastructure.py

stats:
	docker stats --no-stream $$(docker compose ps -q)

docker-stop:
	docker compose stop
