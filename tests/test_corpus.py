"""Authentication, pinned import boundaries and provenance-aware exploration."""

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, Mock

from fastapi.testclient import TestClient
from neo4j import AsyncGraphDatabase, GraphDatabase
import pytest

from app.config import Settings
from app.corpus.api import get_corpus
from app.corpus.service import CorpusConflict, CorpusService, import_corpus
from app.main import create_app
from app.mentions.source import fingerprint, snapshot

TOKEN = "synthetic-test-token-with-32-characters"


@pytest.fixture
def corpus_client(monkeypatch):
    worker = Mock(return_value=dict(status="ALREADY_PRESENT"))
    monkeypatch.setattr("app.corpus.api.import_corpus", worker)
    app = create_app(Settings(neo4j_password="synthetic-password-only", corpus_import_token=TOKEN))
    graph = SimpleNamespace(catalog=AsyncMock(return_value=[]), topic=AsyncMock())
    app.dependency_overrides[get_corpus] = lambda: graph
    with TestClient(app) as client:
        yield client, worker, graph


@pytest.mark.parametrize("credential,status", [(None, 401), ("wrong-token", 403), (TOKEN, 200)])
def test_import_authentication(corpus_client, credential, status):
    client, worker, _ = corpus_client
    response = client.post(
        "/api/corpus/import", json={}, headers={} if credential is None else {"Authorization": f"Bearer {credential}"}
    )
    assert response.status_code == status
    assert worker.call_count == int(status == 200)
    assert TOKEN not in response.text


def test_unconfigured_import_is_disabled():
    with TestClient(create_app(Settings(neo4j_password="synthetic-password-only"))) as client:
        assert client.post("/api/corpus/import", json={}).status_code == 503


@pytest.mark.parametrize(
    "body",
    [
        {"path": "/tmp/arbitrary.pdf"},
        {"corpus": "other"},
        {"sample_per_paper": 2},
        {"sample_per_paper": True},
        {"cypher": "DELETE n"},
    ],
)
def test_import_rejects_unrestricted_input(corpus_client, body):
    client, worker, _ = corpus_client
    assert client.post("/api/corpus/import", json=body, headers={"Authorization": f"Bearer {TOKEN}"}).status_code == 422
    worker.assert_not_called()


def test_import_conflict_and_failure_are_not_success(corpus_client):
    client, worker, _ = corpus_client
    headers = {"Authorization": f"Bearer {TOKEN}"}
    worker.side_effect = CorpusConflict("Partial corpus")
    assert client.post("/api/corpus/import", json={}, headers=headers).status_code == 409
    worker.side_effect = None
    worker.return_value = dict(status="FAILED", import_status="FAILED")
    assert client.post("/api/corpus/import", json={}, headers=headers).status_code == 503
    client.app.state.import_lock = SimpleNamespace(locked=lambda: True)
    assert client.post("/api/corpus/import", json={}, headers=headers).status_code == 409


def test_exploration_validation_and_catalog(corpus_client):
    client, _, graph = corpus_client
    assert client.get("/api/corpus").json() == {"papers": []}
    assert client.get("/api/topics/method:leiden/graph?depth=3").status_code == 422
    assert client.get("/api/topics/DELETE%20n/graph").status_code == 422
    graph.topic.assert_not_called()


@pytest.mark.parametrize(
    "existing,expected", [("complete", "ALREADY_PRESENT"), ("partial", "conflict"), ("empty", "SUCCEEDED")]
)
def test_fixed_import_service_preflight(monkeypatch, existing, expected):
    manifest = [dict(paper_id="a", pdf_access=dict(sha256="hash"))]
    monkeypatch.setattr("app.corpus.service.prototype_manifest", lambda _: manifest)
    record = dict(paper_id="a", pdf_sha256="hash", chunks=2, parse_status="PARSED_NOT_VISUALLY_REVIEWED")
    rows = [] if existing == "empty" else [dict(record, chunks=0)] if existing == "partial" else [record]
    driver = MagicMock()
    driver.session.return_value.__enter__.return_value.run.return_value.data.return_value = rows
    factory = MagicMock()
    factory.return_value.__enter__.return_value = driver
    monkeypatch.setattr("app.corpus.service.GraphDatabase.driver", factory)
    ingest = Mock(
        return_value=dict(
            overall_status="SUCCEEDED", run_id="synthetic", import_status="SUCCEEDED", extraction_status="NOT_REQUESTED"
        )
    )
    monkeypatch.setattr("app.corpus.service.run", ingest)
    settings = Settings(neo4j_password="synthetic-password-only")
    if expected == "conflict":
        with pytest.raises(CorpusConflict):
            import_corpus(settings, 0)
    else:
        assert import_corpus(settings, 0)["status"] == expected
    assert ingest.call_count == int(existing == "empty")


@pytest.mark.integration
def test_existing_corpus_import_is_read_only_and_topic_has_real_support():
    settings = Settings.from_environment()
    with GraphDatabase.driver(
        settings.neo4j_uri, auth=(settings.neo4j_user, settings.neo4j_password.get_secret_value())
    ) as driver:
        before = fingerprint(snapshot(driver))
        assert import_corpus(settings, 0)["status"] == "ALREADY_PRESENT"

        async def exercise():
            async with AsyncGraphDatabase.driver(
                settings.neo4j_uri, auth=(settings.neo4j_user, settings.neo4j_password.get_secret_value())
            ) as async_driver:
                graph = CorpusService(async_driver, settings)
                result = await graph.topic("method:leiden", 2)
                assert result["supports"] and result["evidence"]
                assert {n["label"] for n in result["nodes"]} == {"Entity", "Claim", "Paper"}
                shallow = await graph.topic("method:leiden", 1)
                assert {e["type"] for e in shallow["edges"]} == {"OBJECT"}

        asyncio.run(exercise())
        assert fingerprint(snapshot(driver)) == before
