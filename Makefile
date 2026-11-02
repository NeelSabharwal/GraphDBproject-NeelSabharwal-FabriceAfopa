.PHONY: help configure configure-auth venv install run docker-build docker-run status health models-pull models-check test unit lint format clean tree notebook smoke stats docker-stop ingest embed

# Host Python stays untouched. The local .venv uses the pinned container's Python 3.12.
PYRUN = docker compose run --rm --no-deps -T --user "$$(id -u):$$(id -g)" -v "$(CURDIR):/workspace:ro" -v "$(CURDIR)/data:/workspace/data:ro" -v "$(CURDIR)/data/processed:/workspace/data/processed" -w /workspace --entrypoint .venv/bin/python api
PYWRITE = docker compose run --rm --no-deps -T --user "$$(id -u):$$(id -g)" -v "$(CURDIR):/workspace" -w /workspace --entrypoint python api
VENVWRITE = docker compose run --rm --no-deps -T --user "$$(id -u):$$(id -g)" -v "$(CURDIR):/workspace" -w /workspace --entrypoint .venv/bin/python api

help:
	@printf '%s\n' 'configure     Generate ignored local .env (preserves existing file)' 'docker-build  Build pinned API and Neo4j/GDS images' 'docker-run    Start the three local services (pull models separately)' 'models-pull   Download approved model tags, then verify manifest digests' 'models-check  Compare installed models with models.lock.json' 'status        Show Compose service status' 'health        Check live/ready; fails if dependencies/models unavailable' 'stats         Show one container resource snapshot' 'test          Run unit and real-dependency tests with coverage in API container' 'smoke         Run actual CPU inference/JSON/tool/embedding and Bolt/GDS smoke tests' 'docker-stop   Stop this stack without removing data volumes'
	@printf '%s\n' 'ingest        Verify/import three prototype PDFs; one cached Ollama sample per paper'
	@printf '%s\n' 'embed         Create/reuse pinned Chunk embeddings and verify the vector index'
	@printf '%s\n' 'configure-auth Generate an ignored import token; existing setting preserved' 'venv          Create .venv using pinned Docker Python (requires API image)' 'install       Install the dependency lock into the container-managed .venv' 'run           Start the API on localhost:8000 with existing dependencies' 'unit          Unit/API tests without live-dependency cases' 'lint          Pylint app and scripts; minimum score 9.5' 'format        Black application, operator scripts and tests' 'clean         Remove Python/test caches only; preserve all data' 'tree          Show tracked/source tree to depth three' 'notebook      Execute demo.ipynb; output remains ignored'

configure-auth:
	python3 -m scripts.configure_auth

venv:
	@mkdir -p data/processed
	$(PYWRITE) -c "from pathlib import Path; import venv; p=Path('.venv'); venv.EnvBuilder(with_pip=True).create(p) if not p.exists() else print('Existing .venv preserved')"

install: venv
	$(VENVWRITE) -m pip install --no-cache-dir -r requirements.lock.txt

run:
	docker compose up -d --wait --wait-timeout 180 api

lint:
	$(PYRUN) -m pylint --rcfile=.pylintrc --fail-under=9.5 app scripts

format:
	$(VENVWRITE) -m black --line-length=120 app scripts tests

clean:
	python3 -m scripts.workspace clean

tree:
	python3 -m scripts.workspace tree

unit:
	@mkdir -p data/processed
	$(PYRUN) -m pytest -m 'not integration' --cov=app --cov-fail-under=60 --cov-report=term-missing --cov-report=xml:data/processed/unit-coverage.xml

notebook:
	$(PYRUN) -m scripts.execute_notebook

embed:
	docker compose exec -T api python -m scripts.embed_chunks

configure:
	python3 scripts/configure.py

docker-build:
	docker compose build

docker-run:
	docker compose up -d --build --wait --wait-timeout 180

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
	$(PYRUN) -m pytest --cov=app --cov-fail-under=60 --cov-report=term-missing --cov-report=xml:data/processed/coverage.xml

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
