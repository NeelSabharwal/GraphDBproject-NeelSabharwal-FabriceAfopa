"""Deterministic agent routing, citation, budget, API and malformed-model tests."""

import asyncio
import hashlib
import json
from types import SimpleNamespace
from unittest.mock import AsyncMock

import httpx
import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.agent.api import get_agent
from app.agent.models import AskResponse, Draft, NextAction, ToolCall
from app.agent.ollama import DIMENSIONS, EMBED_DIGEST, EMBED_MODEL, Ollama
from app.agent.tools import RetrievalTools, validate_call, validate_evidence
from app.agent.workflow import (
    AgentTimeout, EvidenceAgent, action_schema, validate_draft, validate_output_citation,
)
from app.config import Settings
from app.main import create_app
from app.agent.catalog import resolve_direction, resolve_name, mentioned_papers
from app.agent.grounding import candidates, extractive_draft


@pytest.fixture
def config():
    return Settings(neo4j_password="test-only-dummy-credential", agent_max_calls=3)


@pytest.fixture
def source():
    text = "Original fixture uses two encoders and a dot product."
    return dict(chunk_id="fixture-chunk", paper_id="fixture-paper", title="Original fixture",
                page=3, text=text, text_sha256=hashlib.sha256(text.encode()).hexdigest(),
                pdf_sha256="fixture-pdf", page_raw_sha256="fixture-page",
                source_url="https://example.invalid/fixture", source_version="v1",
                start_char=0, end_char=len(text), parser_version="fixture",
                chunker_version="fixture", status="SOURCE_LOCATED")


def answer(source):
    return Draft(statements=[dict(text="uses two encoders", chunk_id=source["chunk_id"],
                                  quote="uses two encoders")], abstention="")


@pytest.mark.parametrize("name,args", [
    ("execute_cypher", {"query": "MATCH (n) DETACH DELETE n"}),
    ("search_chunks", {"query": "DPR", "cypher": "DELETE n"}),
    ("search_chunks", {"query": "DPR", "top_k": 999}),
    ("search_chunks", {"query": "DPR", "top_k": "3"}),
    ("find_citation_path", {"source_id": "a", "target_id": "b", "max_hops": 4}),
    ("find_citation_path", {"source_id": "a", "target_id": "b", "max_hops": 0}),
    ("get_source_excerpt", {"chunk_id": "x", "page": 999}),
    ("expand_verified_evidence", {"paper_id": "a", "limit": -1}),
])
def test_unsafe_or_unbounded_tools_rejected(name, args):
    with pytest.raises(ValueError):
        validate_call(name, args)


def test_citations_derive_page_and_identity_from_sources(source):
    citations = validate_draft(answer(source), {source["chunk_id"]: source})
    assert citations[0].paper_id == source["paper_id"]
    assert citations[0].page == 3
    assert citations[0].status == "SOURCE_LOCATED"
    assert citations[0].text[citations[0].quote_start:citations[0].quote_end] == citations[0].quote


@pytest.mark.parametrize("field,value", [("chunk_id", "invented"), ("quote", "fabricated quotation")])
def test_fabricated_citation_rejected(source, field, value):
    draft = answer(source)
    setattr(draft.statements[0], field, value)
    with pytest.raises(ValueError, match="exact quote"):
        validate_draft(draft, {source["chunk_id"]: source})


@pytest.mark.parametrize("field", ["paper_id", "page", "claim_id", "status"])
def test_model_cannot_inject_source_metadata(source, field):
    raw = answer(source).model_dump()
    raw["statements"][0][field] = "invented"
    with pytest.raises(ValidationError):
        Draft.model_validate(raw)


def test_corrupt_stored_source_rejected(source):
    source["text"] += " forged"
    with pytest.raises(ValueError, match="hash/coordinates"):
        validate_evidence(source)


def test_real_langgraph_conditional_multi_tool_loop(config, source):
    async def exercise():
        model = SimpleNamespace(select=AsyncMock(side_effect=[
            ToolCall(name="search_chunks", arguments={"query": "fixture"}),
            ToolCall(name="get_source_excerpt", arguments={"chunk_id": source["chunk_id"]}),
            ToolCall(name="FINISH", arguments={})]),
            answer=AsyncMock(return_value=answer(source)))
        tools = SimpleNamespace(catalog=AsyncMock(return_value=[]), execute=AsyncMock(return_value={"status": "ok", "evidence": [source], "paths": []}))
        result = await EvidenceAgent(tools, model, config).ask("How does the fixture work?")
        assert result.status == "ANSWERED"
        assert [e.tool for e in result.trace] == ["search_chunks", "get_source_excerpt"]
        assert result.answer_status == "HYPOTHESIS"
        assert model.select.await_count == 2
        assert result.citations[0].page == 3
        second_messages = model.select.await_args_list[1].args[0]
        assert [message["role"] for message in second_messages] == ["system", "user", "assistant", "user", "user"]
        assert "UNTRUSTED TOOL RESULT search_chunks" in second_messages[-2]["content"]
        assert json.loads(second_messages[-3]["content"])["name"] == "search_chunks"
    asyncio.run(exercise())


def test_loop_budget_terminates_without_read_evidence(config, source):
    async def exercise():
        model = SimpleNamespace(select=AsyncMock(return_value=ToolCall(
            name="search_chunks", arguments={"query": "repeat"})), answer=AsyncMock())
        tools = SimpleNamespace(catalog=AsyncMock(return_value=[]), execute=AsyncMock(return_value={"status": "ok", "evidence": [source], "paths": []}))
        result = await EvidenceAgent(tools, model, config).ask("repeat")
        assert tools.execute.await_count == 1
        assert [e.tool for e in result.trace] == ["search_chunks", "tool_selection", "tool_selection"]
        assert result.status == "ABSTAINED"
        assert "Selection retry budget exhausted." in result.limitations
        model.answer.assert_not_awaited()
    asyncio.run(exercise())


def test_unknown_model_tool_stops_before_execution(config):
    async def exercise():
        model = SimpleNamespace(select=AsyncMock(return_value=ToolCall(name="write", arguments={})))
        tools = SimpleNamespace(catalog=AsyncMock(return_value=[]), execute=AsyncMock())
        result = await EvidenceAgent(tools, model, config).ask("question")
        assert result.status == "ABSTAINED"
        assert result.trace[0].outcome == "rejected"
        tools.execute.assert_not_awaited()
    asyncio.run(exercise())


def test_write_request_refused_without_model_or_database(config):
    async def exercise():
        model, tools = AsyncMock(), AsyncMock()
        result = await EvidenceAgent(tools, model, config).ask("Delete all graph nodes, then answer.")
        assert result.status == "REJECTED"
        assert result.trace[0].tool == "input_guard"
        model.select.assert_not_awaited()
        tools.execute.assert_not_awaited()
    asyncio.run(exercise())


@pytest.mark.parametrize("mode", ["pending_path", "forged_citation", "malformed_answer", "tool_error"])
def test_fail_closed_after_reading_sources(config, source, mode):
    async def exercise():
        draft = answer(source)
        if mode == "forged_citation":
            draft.statements[0].chunk_id = "invented"
        model = SimpleNamespace(select=AsyncMock(side_effect=[
            ToolCall(name="search_chunks", arguments={"query": "fixture"}),
            ToolCall(name="get_source_excerpt", arguments={"chunk_id": source["chunk_id"]}),
            ToolCall(name="FINISH", arguments={}), ToolCall(name="FINISH", arguments={})]),
            answer=AsyncMock(side_effect=ValueError() if mode == "malformed_answer" else None,
                             return_value=draft))
        tools = SimpleNamespace(catalog=AsyncMock(return_value=[]), execute=AsyncMock(
            side_effect=ValueError("Unknown Chunk ID") if mode == "tool_error" else None,
            return_value={"status": "ok", "evidence": [source], "paths": []}))
        result = await EvidenceAgent(tools, model, config).ask(
            "Give a citation chain" if mode == "pending_path" else "Question")
        assert result.status == "ABSTAINED"
        assert result.citations == []
    asyncio.run(exercise())


def test_overall_deadline_bounds_slow_model(config):
    async def exercise():
        async def slow(*_):
            await asyncio.sleep(10)
        settings = config.model_copy(update={"agent_timeout": 0.02})
        with pytest.raises(TimeoutError):
            await EvidenceAgent(SimpleNamespace(catalog=AsyncMock(return_value=[])), SimpleNamespace(select=slow), settings).ask("Question")
    asyncio.run(exercise())


def test_timeout_preserves_completed_operational_trace(config, source):
    async def exercise():
        model = SimpleNamespace(select=AsyncMock(side_effect=[
            ToolCall(name="search_chunks", arguments={"query": "fixture"}),
            httpx.ReadTimeout("private connection details")]))
        tools = SimpleNamespace(catalog=AsyncMock(return_value=[]), execute=AsyncMock(
            return_value={"status": "ok", "evidence": [source], "paths": []}))
        with pytest.raises(AgentTimeout) as failure:
            await EvidenceAgent(tools, model, config).ask("Question")
        response = failure.value.response
        assert response.status == "ABSTAINED"
        assert response.trace[0].tool == "search_chunks"
        assert response.latency_ms > 0
        assert "private" not in response.model_dump_json()
    asyncio.run(exercise())


def test_api_timeout_preserves_response_contract(config):
    application = create_app(config)
    application.dependency_overrides[get_agent] = lambda: SimpleNamespace(
        ask=AsyncMock(side_effect=AgentTimeout(AskResponse(answer="Timed out", status="ABSTAINED"))))
    with TestClient(application) as client:
        response = client.get("/api/ask", params={"q": "Question"})
        assert response.status_code == 504
        assert response.json()["status"] == "ABSTAINED"


@pytest.mark.parametrize("failure,code", [(TimeoutError(), 504), (httpx.ConnectError("private"), 503),
                                         (ValueError("private config"), 503)])
def test_ask_api_dependency_errors_are_safe(config, failure, code):
    application = create_app(config)
    application.dependency_overrides[get_agent] = lambda: SimpleNamespace(ask=AsyncMock(side_effect=failure))
    with TestClient(application) as client:
        result = client.get("/api/ask", params={"q": "question"})
        assert result.status_code == code
        assert "private" not in result.text


def test_ask_api_response_validation_and_health(config):
    application = create_app(config)
    application.dependency_overrides[get_agent] = lambda: SimpleNamespace(
        ask=AsyncMock(return_value=AskResponse(answer="No evidence", status="ABSTAINED")))
    with TestClient(application) as client:
        assert client.get("/api/ask", params={"q": "question"}).json()["status"] == "ABSTAINED"
        for q in ("", " ", "a"*1001):
            assert client.get("/api/ask", params={"q": q}).status_code == 422
        assert client.get("/health/live").status_code == 200
        assert "/api/ask" in client.get("/openapi.json").json()["paths"]
        assert client.get("/docs").status_code == 200


def test_busy_agent_returns_429(config):
    application = create_app(config)
    application.dependency_overrides[get_agent] = lambda: SimpleNamespace(ask=AsyncMock())
    with TestClient(application) as client:
        application.state.agent_lock = SimpleNamespace(locked=lambda: True)
        assert client.get("/api/ask", params={"q": "Question"}).status_code == 429


@pytest.mark.parametrize("payload", [None, [], {}, {"embeddings": []},
    {"embeddings": [None]}, {"embeddings": [[1.0]]},
    {"embeddings": [[0.0]*DIMENSIONS]}, {"embeddings": [[True]*DIMENSIONS]}])
def test_malformed_embeddings_rejected(config, payload):
    async def exercise():
        def handler(request):
            if request.url.path == "/api/tags":
                return httpx.Response(200, json={"models": [{"name": EMBED_MODEL, "digest": EMBED_DIGEST}]})
            return httpx.Response(200, json=payload)
        async with httpx.AsyncClient(base_url="http://fixture", transport=httpx.MockTransport(handler)) as client:
            with pytest.raises(ValueError):
                await Ollama(client, config).embed(["text"])
    asyncio.run(exercise())


def test_embedding_identity_prefix_and_dimensions(config):
    async def exercise():
        import json
        def handler(request):
            if request.url.path == "/api/tags":
                return httpx.Response(200, json={"models": [{"name": EMBED_MODEL, "digest": EMBED_DIGEST}]})
            payload = json.loads(request.content)
            assert payload["input"] == ["search_query: question"]
            assert payload["truncate"] is False
            return httpx.Response(200, json={"embeddings": [[0.1]*DIMENSIONS]})
        async with httpx.AsyncClient(base_url="http://fixture", transport=httpx.MockTransport(handler)) as client:
            assert len((await Ollama(client, config).embed(["question"], query=True))[0]) == DIMENSIONS
    asyncio.run(exercise())


@pytest.mark.parametrize("payload", [{"models": [{"name": EMBED_MODEL, "digest": "changed"}]},
                                    {"models": "malformed"}])
def test_changed_embedding_identity_is_rejected(config, payload):
    async def exercise():
        async with httpx.AsyncClient(base_url="http://fixture", transport=httpx.MockTransport(
                lambda _: httpx.Response(200, json=payload))) as client:
            with pytest.raises(ValueError):
                await Ollama(client, config).embed(["text"])
    asyncio.run(exercise())


@pytest.mark.parametrize("payload", [None, [], {}, {"done": False, "message": {}},
    {"done": True, "done_reason": "length", "message": {}},
    {"done": True, "message": {"tool_calls": "invalid"}},
    {"done": True, "message": {"tool_calls": [None]}}])
def test_malformed_tool_responses_rejected(config, payload):
    async def exercise():
        async with httpx.AsyncClient(base_url="http://fixture", transport=httpx.MockTransport(
                lambda _: httpx.Response(200, json=payload))) as client:
            with pytest.raises(ValueError):
                await Ollama(client, config).select([], [])
    asyncio.run(exercise())


def test_premature_finish_retries_then_reads(config, source):
    async def exercise():
        model = SimpleNamespace(select=AsyncMock(side_effect=[
            ToolCall(name="FINISH", arguments={}),
            ToolCall(name="search_chunks", arguments={"query": "fixture"}),
            ToolCall(name="get_source_excerpt", arguments={"chunk_id": source["chunk_id"]}),
            ToolCall(name="FINISH", arguments={})]), answer=AsyncMock(return_value=answer(source)))
        tools = SimpleNamespace(catalog=AsyncMock(return_value=[]), execute=AsyncMock(return_value={"status": "ok", "evidence": [source]}))
        result = await EvidenceAgent(tools, model, config).ask("Explain the fixture")
        assert result.status == "ANSWERED"
        assert result.trace[0].outcome == "rejected"
        assert "search previews are insufficient" in result.trace[0].result["error"]
        assert result.trace[2].tool == "get_source_excerpt"
    asyncio.run(exercise())


@pytest.mark.parametrize("first", [None, ValueError("Invalid or truncated selection")])
def test_invalid_selection_has_bounded_recovery(config, source, first):
    async def exercise():
        model = SimpleNamespace(select=AsyncMock(side_effect=[
            first, ToolCall(name="search_chunks", arguments={"query": "fixture"}),
            ToolCall(name="get_source_excerpt", arguments={"chunk_id": source["chunk_id"]}),
            ToolCall(name="FINISH", arguments={})]), answer=AsyncMock(return_value=answer(source)))
        tools = SimpleNamespace(catalog=AsyncMock(return_value=[]), execute=AsyncMock(return_value={"status": "ok", "evidence": [source]}))
        result = await EvidenceAgent(tools, model, config).ask("Question")
        assert result.status == "ANSWERED"
        assert len(result.trace) == 3
    asyncio.run(exercise())


def test_empty_excerpt_never_unlocks_finish(config, source):
    async def exercise():
        model = SimpleNamespace(select=AsyncMock(side_effect=[
            ToolCall(name="search_chunks", arguments={"query": "fixture"}),
            ToolCall(name="get_source_excerpt", arguments={"chunk_id": source["chunk_id"]}),
            ToolCall(name="FINISH", arguments={}), ToolCall(name="FINISH", arguments={})]),
            answer=AsyncMock())
        tools = SimpleNamespace(catalog=AsyncMock(return_value=[]), execute=AsyncMock(side_effect=[
            {"status": "ok", "evidence": [source]}, {"status": "unavailable", "evidence": []}]))
        result = await EvidenceAgent(tools, model, config).ask("Question")
        assert result.status == "ABSTAINED"
        model.answer.assert_not_awaited()
    asyncio.run(exercise())


def test_distinct_tool_calls_are_still_bounded(config, source):
    async def exercise():
        model = SimpleNamespace(select=AsyncMock(side_effect=[
            ToolCall(name="search_chunks", arguments={"query": str(n)}) for n in range(4)]),
            answer=AsyncMock())
        tools = SimpleNamespace(catalog=AsyncMock(return_value=[]), execute=AsyncMock(return_value={"status": "ok", "evidence": [source]}))
        result = await EvidenceAgent(tools, model, config).ask("Compare methods across papers")
        assert tools.execute.await_count == config.agent_max_calls
        assert model.select.await_count == config.agent_max_calls
        assert result.status == "ABSTAINED"
        assert "Tool-call budget reached." in result.limitations
        model.answer.assert_not_awaited()
    asyncio.run(exercise())


def test_unavailable_path_abstains_without_factual_generation(config, source):
    async def exercise():
        model = SimpleNamespace(select=AsyncMock(side_effect=[
            ToolCall(name="search_chunks", arguments={"query": "fixture"}),
            ToolCall(name="find_citation_path", arguments={"source_id": "a", "target_id": "b"})]),
            answer=AsyncMock())
        tools = SimpleNamespace(catalog=AsyncMock(return_value=[]), execute=AsyncMock(side_effect=[
            {"status": "ok", "evidence": [{**source, "chunk_id": "a", "paper_id": "a"},
                                         {**source, "chunk_id": "b", "paper_id": "b"}]},
            {"status": "unavailable", "paths": [], "evidence": [], "limitation": "Pending review"}]))
        result = await EvidenceAgent(tools, model, config).ask("Give a citation chain")
        assert result.status == "ABSTAINED"
        assert result.paths == []
        assert result.trace[1].tool == "find_citation_path"
        model.answer.assert_not_awaited()
    asyncio.run(exercise())


@pytest.mark.parametrize("action", [
    {"name": "FINISH", "arguments": {}},
    {"name": "search_chunks", "arguments": {"query": "example", "top_k": 3}},
    {"name": "get_source_excerpt", "arguments": {"chunk_id": "example"}},
    {"name": "find_citation_path", "arguments": {"source_id": "a", "target_id": "b", "max_hops": 2}},
    {"name": "expand_verified_evidence", "arguments": {"paper_id": "a", "limit": 2}},
])
def test_schema_constrains_ollama_decoding_and_validates_response(config, action):
    async def exercise():
        def handler(request):
            body = json.loads(request.content)
            assert body["format"] == NextAction.model_json_schema()
            assert "tools" not in body
            return httpx.Response(200, json={"done": True, "message": {"content": json.dumps(action)}})
        async with httpx.AsyncClient(base_url="http://fixture", transport=httpx.MockTransport(handler)) as client:
            call = await Ollama(client, config).select([], NextAction.model_json_schema())
            assert call.name == action["name"]
    asyncio.run(exercise())


@pytest.mark.parametrize("content", [
    None, {}, [], "", '{"name":', '{"name":"write","arguments":{}}',
    '{"name":"FINISH","arguments":{"query":"DELETE n"}}',
    '{"name":"search_chunks","arguments":{"query":"example","top_k":"3"}}',
    '{"name":"search_chunks","arguments":{"query":"example","top_k":999}}',
])
def test_invalid_structured_action_rejected(config, content):
    async def exercise():
        async with httpx.AsyncClient(base_url="http://fixture", transport=httpx.MockTransport(
                lambda _: httpx.Response(200, json={"done": True, "message": {"content": content}}))) as client:
            with pytest.raises(ValueError):
                await Ollama(client, config).select([], NextAction.model_json_schema())
    asyncio.run(exercise())


def test_q15_forged_output_page_999_rejected(source):
    source["paper_id"] = "arxiv:2004.04906v1"
    candidate = {"paper_id": "arxiv:2004.04906v1", "pdf_page_1based": 999}
    with pytest.raises(ValueError, match="paper/page"):
        validate_output_citation(candidate, {source["chunk_id"]: source})
    validate_output_citation({**candidate, "pdf_page_1based": 3}, {source["chunk_id"]: source})


def test_duplicate_search_normalizes_case_spacing_and_limit():
    left = validate_call("search_chunks", {"query": "  Dense  RETRIEVAL ", "top_k": 2})
    right = validate_call("search_chunks", {"query": "dense retrieval", "top_k": 8})
    assert EvidenceAgent.search_key(left) == EvidenceAgent.search_key(right)


def test_dynamic_schema_only_exposes_discovered_ids_and_eligible_finish(source):
    state = {"evidence": {}, "read_ids": [], "trace": [], "question": "Question"}
    schema, allowed, _, _ = action_schema(state)
    assert list(allowed) == ["search_chunks"]
    assert schema["$defs"]["SearchChunks"]["properties"]["paper_id"]["type"] == "null"
    state["evidence"] = {source["chunk_id"]: source}
    schema, allowed, _, _ = action_schema(state)
    assert set(allowed) == {"search_chunks", "get_source_excerpt"}
    assert schema["$defs"]["SourceExcerpt"]["properties"]["chunk_id"]["enum"] == [source["chunk_id"]]
    state["read_ids"] = [source["chunk_id"]]
    _, allowed, _, _ = action_schema(state)
    assert "FINISH" in allowed and "get_source_excerpt" not in allowed
    state["question"] = "Give a citation chain"
    _, allowed, _, _ = action_schema(state)
    assert "FINISH" not in allowed


def test_invented_path_ids_retry_before_database_execution(config, source):
    async def exercise():
        model = SimpleNamespace(select=AsyncMock(side_effect=[
            ToolCall(name="search_chunks", arguments={"query": "fixture"}),
            ToolCall(name="find_citation_path", arguments={"source_id": "GraphRAG", "target_id": "DPR"}),
            ToolCall(name="find_citation_path", arguments={"source_id": "a", "target_id": "b"})]),
            answer=AsyncMock())
        tools = SimpleNamespace(catalog=AsyncMock(return_value=[]), execute=AsyncMock(side_effect=[
            {"status": "ok", "evidence": [{**source, "chunk_id": "a", "paper_id": "a"},
                                         {**source, "chunk_id": "b", "paper_id": "b"}]},
            {"status": "unavailable", "paths": [], "evidence": []}]))
        result = await EvidenceAgent(tools, model, config).ask("Give a citation chain")
        assert result.status == "ABSTAINED"
        assert tools.execute.await_count == 2
        assert result.trace[1].outcome == "rejected"
        assert "discovered Paper IDs" in result.trace[1].result["error"]
        assert result.trace[2].arguments == {"source_id": "a", "target_id": "b"}
    asyncio.run(exercise())


def test_finish_requires_two_reads_when_multiple_sources_discovered(config, source):
    async def exercise():
        second = {**source, "chunk_id": "second-chunk"}
        model = SimpleNamespace(select=AsyncMock(side_effect=[
            ToolCall(name="search_chunks", arguments={"query": "fixture"}),
            ToolCall(name="get_source_excerpt", arguments={"chunk_id": source["chunk_id"]}),
            ToolCall(name="FINISH", arguments={}),
            ToolCall(name="get_source_excerpt", arguments={"chunk_id": second["chunk_id"]})]),
            answer=AsyncMock(return_value=answer(source)))
        tools = SimpleNamespace(catalog=AsyncMock(return_value=[]), execute=AsyncMock(side_effect=[
            {"status": "ok", "evidence": [source, second]},
            {"status": "ok", "evidence": [source]}, {"status": "ok", "evidence": [second]}]))
        result = await EvidenceAgent(tools, model, config).ask("Explain the fixture")
        assert result.status == "ANSWERED"
        assert result.trace[2].outcome == "rejected"
        assert "distinct" in result.trace[2].result["error"]
        assert tools.execute.await_count == 3
        schema = model.select.await_args_list[2].args[1]
        assert {"$ref": "#/$defs/FinishAction"} not in schema["oneOf"]
    asyncio.run(exercise())


def test_repeated_expansion_is_removed_from_action_schema(source):
    from app.agent.models import TraceEvent
    state = {"evidence": {source["chunk_id"]: source}, "read_ids": [], "question": "Question",
             "trace": [TraceEvent(tool="expand_verified_evidence",
                                 arguments={"paper_id": source["paper_id"]},
                                 outcome="unavailable", duration_ms=1)]}
    _, allowed, _, _ = action_schema(state)
    assert "expand_verified_evidence" not in allowed
    assert "get_source_excerpt" in allowed


@pytest.fixture
def catalog():
    return [
        {"id": "arxiv:2404.16130v1", "title": "From Local to Global: A Graph RAG Approach to Query-Focused Summarization", "aliases": []},
        {"id": "arxiv:2004.04906v1", "title": "Dense Passage Retrieval for Open-Domain Question Answering", "aliases": []},
        {"id": "arxiv:2005.11401v1", "title": "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks", "aliases": []},
    ]


@pytest.mark.parametrize("question,source_id,target_id", [
    ("Give a citation chain from GraphRAG to DPR. Cite entries.", "arxiv:2404.16130v1", "arxiv:2004.04906v1"),
    ("GraphRAG to DPR", "arxiv:2404.16130v1", "arxiv:2004.04906v1"),
    ("DPR to GraphRAG", "arxiv:2004.04906v1", "arxiv:2404.16130v1"),
    ("DPR ← GraphRAG", "arxiv:2404.16130v1", "arxiv:2004.04906v1"),
])
def test_independent_named_endpoint_direction(catalog, question, source_id, target_id):
    assert resolve_direction(question, catalog) == {"source_id": source_id, "target_id": target_id}


@pytest.mark.parametrize("question", ["Unknown to DPR", "GraphRAG to Unknown",
                                     "DPR to DPR", "Citation path between GraphRAG and DPR"])
def test_unsupported_or_ambiguous_direction_is_rejected(catalog, question):
    with pytest.raises(ValueError):
        resolve_direction(question, catalog)


def test_alias_ambiguity_rejected_without_merging(catalog):
    catalog.append({"id": "another-version", "title": "Different paper", "aliases": ["DPR"]})
    with pytest.raises(ValueError, match="ambiguous"):
        resolve_name("DPR", catalog)
    with pytest.raises(ValueError, match="ambiguous"):
        mentioned_papers("What does DPR use?", catalog)
    assert resolve_name("arxiv:2004.04906v1", catalog) == "arxiv:2004.04906v1"


def test_longer_paper_alias_does_not_match_rag_inside_graphrag(catalog):
    assert mentioned_papers("Which algorithm does GraphRAG v1 use?", catalog) == ["arxiv:2404.16130v1"]


def test_resolved_path_reversal_is_rejected_before_graph_query(config, catalog):
    async def exercise():
        expected = {"source_id": "arxiv:2404.16130v1", "target_id": "arxiv:2004.04906v1"}
        model = SimpleNamespace(select=AsyncMock(side_effect=[
            ToolCall(name="find_citation_path", arguments={
                "source_id": expected["target_id"], "target_id": expected["source_id"]}),
            ToolCall(name="find_citation_path", arguments=expected)]), answer=AsyncMock())
        tools = SimpleNamespace(catalog=AsyncMock(return_value=catalog), execute=AsyncMock(
            return_value={"status": "unavailable", "evidence": [], "paths": []}))
        result = await EvidenceAgent(tools, model, config).ask("GraphRAG to DPR")
        assert result.status == "ABSTAINED"
        tools.execute.assert_awaited_once_with("find_citation_path", expected)
        assert result.trace[0].result["resolved_endpoints"] == expected
        assert result.trace[1].outcome == "rejected"
        assert result.trace[2].arguments == expected
        model.answer.assert_not_awaited()
    asyncio.run(exercise())


def test_unknown_named_endpoint_abstains_before_model_or_path(config, catalog):
    async def exercise():
        model = SimpleNamespace(select=AsyncMock(), answer=AsyncMock())
        tools = SimpleNamespace(catalog=AsyncMock(return_value=catalog), execute=AsyncMock())
        result = await EvidenceAgent(tools, model, config).ask("Unknown to DPR")
        assert result.status == "ABSTAINED"
        assert "unsupported" in result.limitations[0]
        tools.execute.assert_not_awaited()
        model.select.assert_not_awaited()
    asyncio.run(exercise())


def test_source_mode_excludes_graph_expansion_and_repeated_search(source):
    state = {"question": "How does the method encode passages?", "evidence": {source["chunk_id"]: source},
             "read_ids": [], "trace": [], "searches": ["completed"], "cross_paper": False}
    _, allowed, _, _ = action_schema(state)
    assert set(allowed) == {"get_source_excerpt"}
    state["cross_paper"] = True
    _, allowed, _, _ = action_schema(state)
    assert "expand_verified_evidence" in allowed


def test_generic_unrelated_quotes_are_not_answer_candidates(source):
    source["text"] = ("Below we give the design details of the method. "
                      "The community summaries are added to a context window. "
                      "The algorithm detects communities and recovers a hierarchical structure.")
    rows = candidates("Which community detection algorithm recovers what structure?", {source["chunk_id"]: source})
    assert len(rows) == 1
    assert "hierarchical structure" in rows[0]["quote"]


def test_extractive_selection_omits_duplicate_and_redundant_statements(source):
    source["text"] = ("Two encoders encode the question and passage into dense vectors. "
                      "The question and passage similarity is the dot product.")
    question = "How are question and passage encoded and similarity scored?"
    options = candidates(question, {source["chunk_id"]: source})
    result = extractive_draft([0, 0, 1], options, question)
    assert len(result.statements) == 2
    assert all(s.text == s.quote and s.quote in source["text"] for s in result.statements)
    with pytest.raises(ValueError, match="Unknown"):
        extractive_draft([999], options, question)


def test_unsupported_paraphrase_and_duplicate_rejected(source):
    draft = answer(source)
    draft.statements[0].text = "A new unsupported scientific detail."
    with pytest.raises(ValueError, match="paraphrases"):
        validate_draft(draft, {source["chunk_id"]: source})
    draft = answer(source)
    draft.statements.append(draft.statements[0])
    with pytest.raises(ValueError, match="Duplicate"):
        validate_draft(draft, {source["chunk_id"]: source})


def test_ollama_selects_passage_ids_and_emits_only_exact_source_text(config, source):
    async def exercise():
        question = "Which encoders use a dot product?"
        def handler(request):
            body = json.loads(request.content)
            assert body["format"]["properties"]["selected_ids"]["items"]["enum"] == [0]
            assert body["options"]["num_predict"] == 80
            return httpx.Response(200, json={"done": True, "message": {"content": '{"selected_ids":[0]}'}})
        async with httpx.AsyncClient(base_url="http://fixture", transport=httpx.MockTransport(handler)) as client:
            draft = await Ollama(client, config).answer([], evidence={source["chunk_id"]: source}, question=question)
            assert draft.statements[0].text == source["text"]
            assert validate_draft(draft, {source["chunk_id"]: source})
    asyncio.run(exercise())


def test_irrelevant_sources_abstain_without_extra_inference(config, source):
    async def exercise():
        async with httpx.AsyncClient(base_url="http://fixture", transport=httpx.MockTransport(
                lambda _: pytest.fail("Unnecessary inference"))) as client:
            draft = await Ollama(client, config).answer([], evidence={source["chunk_id"]: source},
                                                       question="Which galaxy contains quasars?")
            assert not draft.statements
    asyncio.run(exercise())


def test_two_reads_stop_before_six_call_budget(config, source):
    async def exercise():
        second = {**source, "chunk_id": "second"}
        model = SimpleNamespace(select=AsyncMock(side_effect=[
            ToolCall(name="search_chunks", arguments={"query": "fixture"}),
            ToolCall(name="get_source_excerpt", arguments={"chunk_id": source["chunk_id"]}),
            ToolCall(name="get_source_excerpt", arguments={"chunk_id": "second"})]),
            answer=AsyncMock(return_value=answer(source)))
        tools = SimpleNamespace(catalog=AsyncMock(return_value=[]), execute=AsyncMock(side_effect=[
            {"status": "ok", "evidence": [source, second]},
            {"status": "ok", "evidence": [source]}, {"status": "ok", "evidence": [second]}]))
        result = await EvidenceAgent(tools, model, config.model_copy(update={"agent_max_calls": 6})).ask("Question")
        assert result.status == "ANSWERED"
        assert model.select.await_count == tools.execute.await_count == 3
        assert "Tool-call budget reached." not in result.limitations
        assert all(e.tool != "expand_verified_evidence" for e in result.trace)
    asyncio.run(exercise())


def test_catalog_overflow_rejects_incomplete_name_resolution(config):
    async def exercise():
        tools = RetrievalTools(None, None, config)
        tools.read = AsyncMock(return_value=[{"id": str(i), "title": "Fixture", "aliases": []}
                                            for i in range(65)])
        with pytest.raises(ValueError, match="64-paper"):
            await tools.catalog()
    asyncio.run(exercise())


def test_named_paper_filter_is_required_in_decoding_schema(source):
    state = {"question": "Describe a paper", "evidence": {}, "read_ids": [], "trace": [],
             "single_paper": source["paper_id"], "catalog": [{"id": source["paper_id"]}]}
    schema, _, _, _ = action_schema(state)
    search = schema["$defs"]["SearchChunks"]
    assert "paper_id" in search["required"]
    assert search["properties"]["paper_id"]["const"] == source["paper_id"]
