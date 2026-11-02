"""Deterministic smoke-response regressions using HTTP mocks, never real inference."""

import json

import httpx
import pytest

from scripts.smoke import run_ollama_case


@pytest.mark.parametrize(
    "name,payload,expected_detail",
    [
        ("embedding", None, "Ollama response must be a JSON object"),
        ("embedding", [], "Ollama response must be a JSON object"),
        ("text", "unexpected", "Ollama response must be a JSON object"),
        ("embedding", {}, "Expected exactly one embedding vector in an embeddings list"),
        ("embedding", {"embeddings": None}, "Expected exactly one embedding vector in an embeddings list"),
        ("embedding", {"embeddings": []}, "Expected exactly one embedding vector in an embeddings list"),
        ("embedding", {"embeddings": {}}, "Expected exactly one embedding vector in an embeddings list"),
        ("embedding", {"embeddings": [None]}, "Embedding vector must be a list of 768 numbers"),
        ("embedding", {"embeddings": [[]]}, "Embedding vector must be a list of 768 numbers"),
        ("embedding", {"embeddings": ["invalid"]}, "Embedding vector must be a list of 768 numbers"),
        (
            "embedding",
            {"embeddings": [["invalid"] * 768]},
            "Embedding values must be finite numbers, excluding booleans",
        ),
        ("embedding", {"embeddings": [[True] * 768]}, "Embedding values must be finite numbers, excluding booleans"),
        ("embedding", {"embeddings": [[0.0] * 768]}, "Embedding values must be finite with a nonzero finite norm"),
        (
            "embedding",
            {"embeddings": [[float("nan")] * 768]},
            "Embedding values must be finite with a nonzero finite norm",
        ),
        (
            "embedding",
            {"embeddings": [[float("inf")] * 768]},
            "Embedding values must be finite with a nonzero finite norm",
        ),
        ("text", {}, "Chat response must contain a message object"),
        ("text", {"message": []}, "Chat response must contain a message object"),
        ("text", {"message": {"content": None}}, "Chat message content must be a non-empty string"),
        ("text", {"message": {"content": "  "}}, "Chat message content must be a non-empty string"),
        (
            "structured_json",
            {"message": {"content": "not json"}},
            "Structured response must match the project/local_only JSON schema",
        ),
        (
            "structured_json",
            {"message": {"content": "[]"}},
            "Structured response must match the project/local_only JSON schema",
        ),
        (
            "structured_json",
            {"message": {"content": '{"project":"other","local_only":true}'}},
            "Structured response must contain project=GraphRAG and local_only=true",
        ),
        ("tool_call", {"message": {"tool_calls": None}}, "Expected exactly one actual tool call in a tool_calls list"),
        ("tool_call", {"message": {"tool_calls": []}}, "Expected exactly one actual tool call in a tool_calls list"),
        ("tool_call", {"message": {"tool_calls": [None]}}, "Tool call must contain a function object"),
        ("tool_call", {"message": {"tool_calls": [{"function": []}]}}, "Tool call must contain a function object"),
        ("tool_call", {"message": {"tool_calls": [{"function": {"name": "other"}}]}}, "Expected the lookup_paper tool"),
        (
            "tool_call",
            {"message": {"tool_calls": [{"function": {"name": "lookup_paper", "arguments": "invalid"}}]}},
            "Tool arguments must be an object containing paper_id=2005.11401",
        ),
    ],
)
def test_malformed_model_response_is_reported_as_failed_case(name, payload, expected_detail):
    """Malformed nested values become clear failures instead of indexing/type crashes."""

    def respond(request):
        assert request.method == "POST"
        return httpx.Response(200, content=json.dumps(payload))

    with httpx.Client(transport=httpx.MockTransport(respond), base_url="http://ollama") as client:
        result = run_ollama_case(client, name, "/api/chat", {})

    assert result["passed"] is False
    assert result["error"] == "ValueError"
    assert result["detail"] == expected_detail
    assert result["wall_seconds"] >= 0


@pytest.mark.parametrize(
    "name,payload,expected_output",
    [
        ("text", {"message": {"content": "Local response"}}, "Local response"),
        (
            "structured_json",
            {"message": {"content": '{"project":"GraphRAG","local_only":true}'}},
            {"project": "GraphRAG", "local_only": True},
        ),
        (
            "tool_call",
            {
                "message": {
                    "tool_calls": [{"function": {"name": "lookup_paper", "arguments": {"paper_id": "2005.11401"}}}]
                }
            },
            [{"function": {"name": "lookup_paper", "arguments": {"paper_id": "2005.11401"}}}],
        ),
        ("embedding", {"embeddings": [[1.0] + [0.0] * 767]}, {"vectors": 1, "dimensions": 768, "l2_norm": 1.0}),
    ],
)
def test_valid_smoke_responses_still_pass(name, payload, expected_output):
    """Keep successful text, JSON, tool and embedding output contracts intact."""

    def respond(request):
        return httpx.Response(200, json=payload if request.method == "POST" else {"models": []})

    with httpx.Client(transport=httpx.MockTransport(respond), base_url="http://ollama") as client:
        result = run_ollama_case(client, name, "/api/chat", {})

    assert result["passed"] is True
    assert result["output"] == expected_output
    assert result["loaded_models"] == []


@pytest.mark.parametrize("payload", [None, [], {}, {"models": None}])
def test_malformed_loaded_model_metadata_is_reported(payload):
    """A malformed /api/ps payload must not leave the case marked as passed."""

    def respond(request):
        data = {"message": {"content": "Local response"}} if request.method == "POST" else payload
        return httpx.Response(200, content=json.dumps(data))

    with httpx.Client(transport=httpx.MockTransport(respond), base_url="http://ollama") as client:
        result = run_ollama_case(client, "text", "/api/chat", {})

    assert result["passed"] is False
    assert result["detail"] == "Ollama /api/ps response must contain a models list"


@pytest.mark.parametrize("exception_type", [IndexError, TypeError])
def test_unexpected_payload_access_error_is_recorded(exception_type):
    """Defensive fallback errors remain failed cases with useful details."""

    def respond(_request):
        raise exception_type("unexpected response payload")

    with httpx.Client(transport=httpx.MockTransport(respond), base_url="http://ollama") as client:
        result = run_ollama_case(client, "embedding", "/api/embed", {})

    assert result["passed"] is False
    assert result["error"] == exception_type.__name__
    assert result["detail"] == "unexpected response payload"
