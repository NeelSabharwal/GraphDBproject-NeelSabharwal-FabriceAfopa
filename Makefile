.PHONY: help configure docker-build docker-run status health models-pull models-check test smoke stats docker-stop

help:
	@printf '%s\n' 'configure     Generate ignored local .env (preserves existing file)' 'docker-build  Build pinned API and Neo4j/GDS images' 'docker-run    Start the three local services (pull models separately)' 'models-pull   Download approved model tags, then verify manifest digests' 'models-check  Compare installed models with models.lock.json' 'status        Show Compose service status' 'health        Check live/ready; fails if dependencies/models unavailable' 'stats         Show one container resource snapshot' 'test          Run unit and real-dependency tests with coverage in API container' 'smoke         Run actual CPU inference/JSON/tool/embedding and Bolt/GDS smoke tests' 'docker-stop   Stop this stack without removing data volumes'

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
	docker compose exec -T api python -m pytest --cov=app --cov-report=term-missing --cov-report=xml:/tmp/coverage.xml

smoke:
	python3 scripts/verify_infrastructure.py

stats:
	docker stats --no-stream $$(docker compose ps -q)

docker-stop:
	docker compose stop
