"""Bounded API contracts and real GDS/source checks; synthetic changes are isolated."""

import asyncio
from copy import deepcopy
import json
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient
from neo4j import AsyncGraphDatabase
from neo4j.exceptions import ServiceUnavailable
from pydantic import ValidationError

from app.analytics.api import get_graph
from app.analytics.gds import Analytics, ProjectionManager, modularity
from app.analytics.models import AnalyticsResponse, Rank
from app.analytics.service import GraphService, GraphUnavailable, UnknownPaper, accepted_entity, approved
from app.config import Settings
from app.main import create_app
from app.ingestion.graph import EvidenceGraph
from test_reviewed_evidence import research_fixture, live_research  # noqa: F401

DPR, RAG, GRAPHRAG = "arxiv:2004.04906v1", "arxiv:2005.11401v1", "arxiv:2404.16130v1"


def test_alias_identity_requires_qualified_acceptance():
    e = dict(
        id="method:bert-base",
        resolution_status="STUDENT_APPROVED_SCOPED",
        alias_review_json=json.dumps(dict(outcome="ACCEPT", decision="APPROVED", canonical_id="method:bert-base")),
    )
    assert accepted_entity(e)
    for outcome in ("REJECT", "NEEDS_CLARIFICATION"):
        altered = dict(
            e, alias_review_json=json.dumps(dict(outcome=outcome, decision="APPROVED", canonical_id=e["id"]))
        )
        assert not accepted_entity(altered)
    assert not accepted_entity(dict(e, alias_review_json="invalid"))
    assert not accepted_entity(dict(e, alias_review_json="[]"))
    assert not approved(dict(status="SOURCE_VERIFIED", human_reviewed=False))


@pytest.mark.parametrize("papers", [[], ["a", "a"], [str(i) for i in range(17)]])
def test_corpus_budgets(papers):
    with pytest.raises(ValueError):
        GraphService(None, None, papers)


def test_rank_validation_and_modularity():
    with pytest.raises(ValidationError):
        Rank(paper_id=DPR, title="DPR", score=float("nan"), weighted_degree=1)
    assert modularity([], {"a": 1}) == 0
    pair = [dict(source="a", target="b", weight=0.75)]
    assert modularity(pair, {"a": 1, "b": 1, "c": 2}) == 0
    assert modularity(pair, {"a": 1, "b": 2}) == -0.5


@pytest.fixture
def client_graph():
    graph = SimpleNamespace(
        path=AsyncMock(return_value=dict(status="unavailable", paths=[], evidence=[])),
        shared=AsyncMock(),
        related=AsyncMock(),
        run=AsyncMock(),
    )
    app = create_app(Settings(neo4j_password="SYNTHETIC_TEST_PASSWORD"))
    app.dependency_overrides[get_graph] = lambda: graph
    with TestClient(app) as client:
        yield client, graph


def test_api_validation_and_no_write_capabilities(client_graph):
    client, graph = client_graph
    base = f"/api/papers/{GRAPHRAG}/paths"
    assert client.get(base, params={"target_id": DPR}).status_code == 200
    assert client.get(base, params={"target_id": DPR, "max_hops": 4}).status_code == 422
    assert client.get(base, params={"target_id": "MATCH (n) DELETE n"}).status_code == 422
    assert client.get(base, params={"target_id": DPR, "cypher": "DELETE n"}).status_code == 422
    assert client.get("/api/papers/centrality?limit=21").status_code == 422
    assert client.get(f"/api/papers/{DPR}/related?offset=101").status_code == 422
    assert client.get(f"/api/papers/{DPR}/shared?target_id={RAG}&kind=Topic").status_code == 422
    assert client.post(base, json={"target_id": DPR}).status_code == 405
    assert client.post("/api/papers/centrality", json={"operation": "write"}).status_code == 405
    assert client.post("/api/papers/projection/refresh").status_code == 404
    assert graph.path.await_count == 1
    assert not graph.run.called
    assert not hasattr(Analytics, "refresh") and not hasattr(Analytics, "drop")


@pytest.mark.parametrize(
    "error,status",
    [
        (UnknownPaper("unknown"), 404),
        (GraphUnavailable("stale"), 503),
        (ServiceUnavailable("offline"), 503),
        (ValueError("Citation endpoints must be distinct"), 400),
        (ValueError("corrupt evidence"), 503),
    ],
)
def test_api_errors(client_graph, error, status):
    client, graph = client_graph
    graph.path.side_effect = error
    assert client.get(f"/api/papers/{GRAPHRAG}/paths", params={"target_id": DPR}).status_code == status


def test_api_busy_and_response_validation(client_graph):
    client, graph = client_graph
    client.app.state.analytics_lock = SimpleNamespace(locked=lambda: True)
    assert client.get("/api/papers/communities").status_code == 429
    assert not graph.run.called


async def with_service(operation, papers=None):
    config = Settings.from_environment()
    async with AsyncGraphDatabase.driver(
        config.neo4j_uri,
        auth=(config.neo4j_user, config.neo4j_password.get_secret_value()),
        max_transaction_retry_time=0,
    ) as driver:
        return await operation(ProjectionManager(driver, config, papers))


@pytest.mark.integration
def test_real_graph_paths_shared_datasets_and_algorithms():
    async def check(service):
        snap = await service.snapshot()
        assert len(snap["claims"]) == 20 and len(snap["excluded_claim_ids"]) == 3
        assert len(snap["pairs"]) == 1 and snap["pairs"][0]["weight"] == 0.75
        path = await service.path(GRAPHRAG, DPR, 2)
        assert path["paths"][0]["papers"] == [GRAPHRAG, RAG, DPR]
        assert all(
            c["target_version_as_cited"] == "unspecified" for e in path["paths"][0]["edges"] for c in e["claims"]
        )
        assert (await service.path(GRAPHRAG, DPR, 1))["status"] == "unavailable"
        assert (await service.path(DPR, GRAPHRAG, 3))["status"] == "unavailable"
        with pytest.raises(UnknownPaper):
            await service.path("arxiv:9999.99999v1", DPR, 2)
        with pytest.raises(ValueError, match="distinct"):
            await service.path(DPR, DPR, 2)
        shared = await service.shared(DPR, RAG, "Dataset")
        assert {e["entity_id"] for e in shared["entities"]} == {
            "dataset:natural-questions",
            "dataset:triviaqa",
            "dataset:webquestions",
            "dataset:curatedtrec",
        }
        assert all(s["status"] == "SOURCE_VERIFIED" for s in shared["supports"])
        assert len((await service.shared(DPR, RAG, "Dataset", 2, 1))["entities"]) == 2
        assert not (await service.shared(DPR, RAG, "Dataset", 2, 4))["entities"]
        assert not (await service.shared(DPR, GRAPHRAG))["entities"]
        related = await service.related(DPR)
        assert [(p["paper_id"], p["similarity"]) for p in related["papers"]] == [(RAG, 0.75)]
        assert not (await service.related(DPR, 1, 1))["papers"]
        assert not (await service.related(GRAPHRAG))["papers"]
        await service.refresh()
        rank = AnalyticsResponse.model_validate(await service.run("pagerank"))
        assert rank.isolated_papers == [GRAPHRAG]
        scores = {p.paper_id: p.score for p in rank.ranks}
        assert scores[DPR] == pytest.approx(scores[RAG]) and scores[DPR] > scores[GRAPHRAG]
        communities = AnalyticsResponse.model_validate(await service.run("louvain"))
        groups = {p.paper_id: p.community_id for p in communities.memberships}
        assert groups[DPR] == groups[RAG] != groups[GRAPHRAG]
        assert communities.stream_modularity == pytest.approx(communities.stats["modularity"])
        assert (await service.snapshot())["fingerprint"] == snap["fingerprint"]

    asyncio.run(with_service(check))


@pytest.mark.integration
def test_real_fastapi_routes_and_swagger():
    with TestClient(create_app(Settings.from_environment())) as client:
        examples = [
            f"/{GRAPHRAG}/paths?target_id={DPR}",
            f"/{DPR}/shared?target_id={RAG}&kind=Dataset",
            f"/{DPR}/related",
            "/centrality?limit=2",
            "/communities?limit=2",
        ]
        for url in examples:
            response = client.get("/api/papers" + url)
            assert response.status_code == 200, response.text
        assert len(client.get("/api/papers/centrality?limit=2").json()["ranks"]) == 2
        assert client.get("/docs").status_code == 200
        paths = client.get("/openapi.json").json()["paths"]
        assert "/api/papers/communities" in paths
        assert client.get("/api/papers/arxiv:9999.99999v1/related").status_code == 404


@pytest.mark.integration
def test_synthetic_projection_staleness_deduplication_and_isolates(live_research):
    """Only UUID-named synthetic evidence is modified, then existing fixtures clean up."""
    driver, importer = live_research
    before, _ = importer.dry_run()
    importer.apply(before["fingerprint"])
    ids = importer.paper_ids

    async def check(service):
        names = []
        try:
            with pytest.raises(GraphUnavailable, match="missing or stale"):
                await service.run("pagerank")
            first = await service.refresh()
            names.append(first["name"])
            assert first["projection"]["relationships"] == 2
            assert (await service.refresh())["action"] == "REUSED"
            snap = await service.snapshot()
            # Distinct-entity sets deduplicate additional approved assertions/support.
            original = next(c for c in snap["claims"].values() if c["paper_id"] == ids[0])
            duplicate = ids[0] + "-duplicate"
            driver.execute_query(
                "MATCH (c:Claim {id:$id}) CREATE (copy:Claim) SET copy=c {.*,id:$new} "
                "WITH c,copy MATCH (c)-[:SUBJECT]->(p) MATCH (c)-[:OBJECT]->(e) "
                "CREATE (copy)-[:SUBJECT]->(p),(copy)-[:OBJECT]->(e) "
                "WITH c,copy MATCH (c)-[s:SUPPORTED_BY]->(chunk) CREATE (copy)-[t:SUPPORTED_BY]->(chunk) SET t=properties(s)",
                id=original["id"],
                new=duplicate,
            )
            with pytest.raises(GraphUnavailable, match="missing or stale"):
                await service.run("pagerank")
            fresh = await service.refresh()
            names.append(fresh["name"])
            assert len(fresh["adjacencies"]) == 1 and fresh["adjacencies"][0]["weight"] == 0.75
            assert not (await service.tools.read("RETURN gds.graph.exists($name) AS exists", name=first["name"]))[0][
                "exists"
            ]
            # Pending/rejected duplicates cannot create extra scientific identities.
            driver.execute_query(
                'MATCH (c:Claim {id:$id}) SET c.status="REJECTED",c.student_review_status="rejected"', id=duplicate
            )
            with pytest.raises(GraphUnavailable):
                await service.run("louvain")
            rejected = await service.snapshot()
            assert duplicate not in rejected["claims"] and rejected["pairs"][0]["weight"] == 0.75
            driver.execute_query(
                'MATCH (c:Claim {id:$id}) SET c.status="EXTRACTED",c.student_review_status="pending"', id=duplicate
            )
            assert duplicate not in (await service.snapshot())["claims"]
            # Unresolved alias identity must never join this analytical graph.
            entity = original["object_id"]
            driver.execute_query(
                "MATCH (e:Entity {id:$id}) SET e.alias_review_json=$review",
                id=entity,
                review=json.dumps(dict(outcome="NEEDS_CLARIFICATION", decision="APPROVED", canonical_id=entity)),
            )
            assert entity not in (await service.snapshot())["entities"]
            # Finally leave all synthetic scientific claims pending: all vertices survive.
            driver.execute_query(
                'MATCH (c:Claim) WHERE c.paper_id IN $ids AND c.predicate<>"CITES" SET c.status="EXTRACTED",c.student_review_status="pending"',
                ids=ids,
            )
            empty = await service.refresh()
            names.append(empty["name"])
            assert empty["projection"]["nodes"] == 3 and empty["projection"]["relationships"] == 0
            for algo in ("pagerank", "louvain"):
                result = AnalyticsResponse.model_validate(await service.run(algo))
                assert result.isolated_papers == sorted(ids)
            with pytest.raises(ValueError):
                await service.drop("arbitrary_other_graph")
            with pytest.raises(ValueError):
                await service.run("write")
        finally:
            for name in names:
                await service.drop(name)

    asyncio.run(with_service(check, ids))


def test_review_race_and_missing_paper_fail_closed():
    async def check():
        service = GraphService(None, None, [DPR])
        service.tools.read = AsyncMock(return_value=[])
        with pytest.raises(GraphUnavailable, match="missing"):
            await service.records()
        service.records = AsyncMock(return_value=[{"changed": True}])
        with pytest.raises(GraphUnavailable, match="changed"):
            await service.ensure_review_unchanged({"review_state": "old"})

    asyncio.run(check())


@pytest.mark.parametrize("change", ["node_count", "identities", "weights", "orientation"])
def test_corrupt_projection_is_rejected(change):
    async def check():
        service = Analytics(None, None, [DPR, RAG])
        snap = dict(
            fingerprint="a" * 64, papers=[{"id": DPR}, {"id": RAG}], pairs=[dict(source=DPR, target=RAG, weight=0.75)]
        )
        catalog = dict(
            nodeCount=2,
            relationshipCount=2,
            sizeInBytes=100,
            schemaWithOrientation={"relationships": {"SHARES_ENTITY": {"direction": "UNDIRECTED"}}},
        )
        nodes = [dict(nodeId=0, propertyValue=0), dict(nodeId=1, propertyValue=1)]
        edges = [
            dict(sourceNodeId=0, targetNodeId=1, propertyValue=0.75),
            dict(sourceNodeId=1, targetNodeId=0, propertyValue=0.75),
        ]
        if change == "node_count":
            catalog["nodeCount"] = 3
        if change == "identities":
            nodes[0]["propertyValue"] = 5
        if change == "weights":
            edges[0]["propertyValue"] = 0.5
        if change == "orientation":
            catalog["schemaWithOrientation"]["relationships"]["SHARES_ENTITY"]["direction"] = "DIRECTED"
        service.tools.read = AsyncMock(side_effect=[[{"exists": True}], [catalog], nodes, edges])
        with pytest.raises(GraphUnavailable):
            await service.projection(snap)

    asyncio.run(check())
