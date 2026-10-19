"""Health behavior tests; these cases explicitly replace dependency results."""

import asyncio
from types import SimpleNamespace

from fastapi.testclient import TestClient
import httpx
from pydantic import ValidationError
import pytest
from starlette.requests import Request

from app.config import Settings
from app.health import HealthResponse, check_neo4j, check_ollama, check_readiness
from app.main import create_app


@pytest.fixture
def settings():
    """Use a dummy credential only; never access the local .env."""
    return Settings(neo4j_password="test-only-dummy-credential", readiness_timeout=0.1)


def test_liveness_and_swagger_do_not_require_dependencies(settings):
    """Liveness and OpenAPI work even when dependencies are not probed."""
    with TestClient(create_app(settings)) as client:
        assert client.get("/health/live").json() == {"status": "ok", "checks": {}}
        assert client.get("/docs").status_code == 200
        assert "/health/ready" in client.get("/openapi.json").json()["paths"]


@pytest.mark.parametrize("checks", [
    {"neo4j_gds": "unavailable", "ollama": "ok"},
    {"neo4j_gds": "ok", "ollama": "models_missing"},
    {"neo4j_gds": "ok", "ollama": "unavailable"},
    {"neo4j_gds": "ok", "ollama": "ok"},
])
def test_readiness_status_contract(settings, checks):
    """Any unavailable dependency produces 503, with a safe structured response."""
    application = create_app(settings)
    ready = all(value == "ok" for value in checks.values())

    async def fake_checks():
        return HealthResponse(status="ready" if ready else "not_ready", checks=checks)

    application.dependency_overrides[check_readiness] = fake_checks
    with TestClient(application) as client:
        response = client.get("/health/ready")
        assert response.status_code == (200 if ready else 503)
        assert response.json()["checks"] == checks
        assert settings.neo4j_password.get_secret_value() not in response.text


@pytest.mark.parametrize("payload,expected", [
    ({"models": []}, "models_missing"),
    ({"models": [{"name": "qwen2.5:3b-instruct"}, {"name": "nomic-embed-text:v1.5"}]}, "ok"),
    ({"unexpected": True}, "unavailable"),
])
def test_ollama_probe_checks_required_models(settings, payload, expected):
    """A reachable but empty model server cannot make the application ready."""
    async def exercise():
        transport = httpx.MockTransport(lambda _: httpx.Response(200, json=payload))
        async with httpx.AsyncClient(base_url="http://ollama", transport=transport) as client:
            application = SimpleNamespace(state=SimpleNamespace(settings=settings, http=client))
            request = Request({"type": "http", "app": application})
            assert await check_ollama(request) == expected
    asyncio.run(exercise())


def test_database_timeout_is_bounded_and_redacted(settings):
    """An unresponsive dependency cannot hang readiness indefinitely."""
    class SlowDriver:
        """Delay session entry past the configured outer probe deadline."""

        def session(self, **_kwargs):
            return self

        async def __aenter__(self):
            await asyncio.sleep(10)

        async def __aexit__(self, *_args):
            return False

    async def exercise():
        application = SimpleNamespace(state=SimpleNamespace(settings=settings, driver=SlowDriver()))
        request = Request({"type": "http", "app": application})
        assert await asyncio.wait_for(check_neo4j(request), timeout=0.5) == "unavailable"
    asyncio.run(exercise())


def test_configuration_rejects_unbounded_timeout(settings):
    """Misconfigured dependency deadlines fail validation before serving requests."""
    with pytest.raises(ValidationError):
        Settings(neo4j_password=settings.neo4j_password, readiness_timeout=100)
