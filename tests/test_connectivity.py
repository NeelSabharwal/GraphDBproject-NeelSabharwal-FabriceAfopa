"""Real integration tests: no mocks or skips; running Compose services required."""

from fastapi.testclient import TestClient
from neo4j import GraphDatabase
import pytest

from app.config import Settings
from app.main import create_app

pytestmark = pytest.mark.integration


def test_authenticated_bolt_and_gds_procedures():
    """Inspect actual versions and registered procedures without creating a graph."""
    config = Settings.from_environment()
    with GraphDatabase.driver(
        config.neo4j_uri,
        auth=(config.neo4j_user, config.neo4j_password.get_secret_value()),
        connection_timeout=3,
        max_transaction_retry_time=0,
    ) as driver:
        driver.verify_connectivity()
        records, _, _ = driver.execute_query("CALL dbms.components() YIELD versions, edition RETURN versions[0] AS version, edition")
        assert records[0]["version"] == "5.26.32"
        assert records[0]["edition"] == "community"
        records, _, _ = driver.execute_query("RETURN gds.version() AS version")
        assert records[0]["version"] == "2.13.2"
        records, _, _ = driver.execute_query(
            "SHOW PROCEDURES YIELD name WHERE name IN $names RETURN name",
            names=["gds.graph.list", "gds.graph.project", "gds.pageRank.stream", "gds.louvain.stream"],
        )
        assert len(records) == 4
        driver.execute_query("CALL gds.graph.list() YIELD graphName RETURN graphName")


def test_real_dependency_readiness():
    """Both model tags, real Ollama HTTP and authenticated Bolt/GDS must work."""
    with TestClient(create_app()) as client:
        response = client.get("/health/ready")
        assert response.status_code == 200, response.json()
        assert response.json() == {"status": "ready", "checks": {"neo4j_gds": "ok", "ollama": "ok"}}
