"""Real CPU-only model and database smoke checks, executed inside the API image."""

import json
import math
import platform
import time

import fastapi
import httpx
from neo4j import GraphDatabase
from pydantic import BaseModel, ConfigDict

from app.config import Settings


class StructuredProbe(BaseModel):
    """A small schema validates the actual model response, not just JSON syntax."""

    model_config = ConfigDict(extra="forbid", strict=True)
    project: str
    local_only: bool


def validate_ollama_output(name: str, data: object) -> dict:
    """Validate a smoke response explicitly before accessing nested fields."""
    if not isinstance(data, dict):
        raise ValueError("Ollama response must be a JSON object")

    if name == "embedding":
        embeddings = data.get("embeddings")
        if not isinstance(embeddings, list) or len(embeddings) != 1:
            raise ValueError("Expected exactly one embedding vector in an embeddings list")
        vector = embeddings[0]
        if not isinstance(vector, list) or len(vector) != 768:
            raise ValueError("Embedding vector must be a list of 768 numbers")
        if not all(type(value) in (int, float) for value in vector):
            raise ValueError("Embedding values must be finite numbers, excluding booleans")
        try:
            norm = math.hypot(*vector)
        except (OverflowError, TypeError) as error:
            raise ValueError("Embedding values must be finite numbers") from error
        if not all(math.isfinite(value) for value in vector) or not math.isfinite(norm) or norm <= 0:
            raise ValueError("Embedding values must be finite with a nonzero finite norm")
        return {"output": {"vectors": 1, "dimensions": len(vector), "l2_norm": round(norm, 6)}}

    message = data.get("message")
    if not isinstance(message, dict):
        raise ValueError("Chat response must contain a message object")

    if name in {"text", "structured_json"}:
        content = message.get("content")
        if not isinstance(content, str) or not content.strip():
            raise ValueError("Chat message content must be a non-empty string")
        if name == "text":
            return {"output": content}
        try:
            output = StructuredProbe.model_validate_json(content)
        except ValueError as error:
            raise ValueError("Structured response must match the project/local_only JSON schema") from error
        if output.project != "GraphRAG" or output.local_only is not True:
            raise ValueError("Structured response must contain project=GraphRAG and local_only=true")
        return {"output": output.model_dump()}

    if name != "tool_call":
        raise ValueError("Unknown Ollama smoke case")
    calls = message.get("tool_calls")
    if not isinstance(calls, list) or len(calls) != 1:
        raise ValueError("Expected exactly one actual tool call in a tool_calls list")
    call = calls[0]
    if not isinstance(call, dict) or not isinstance(call.get("function"), dict):
        raise ValueError("Tool call must contain a function object")
    function = call["function"]
    if function.get("name") != "lookup_paper":
        raise ValueError("Expected the lookup_paper tool")
    if not isinstance(function.get("arguments"), dict) or function["arguments"] != {"paper_id": "2005.11401"}:
        raise ValueError("Tool arguments must be an object containing paper_id=2005.11401")
    return {
        "output": calls,
        "note": "Tool selection/arguments only; no graph lookup or agent implemented.",
    }


def run_ollama_case(client: httpx.Client, name: str, path: str, payload: dict) -> dict:
    """Turn HTTP or malformed-payload failures into a timed, actionable case result."""
    started = time.perf_counter()
    case = {"name": name}
    try:
        response = client.post(path, json=payload)
        response.raise_for_status()
        data = response.json()
        case.update(validate_ollama_output(name, data))
        loaded_response = client.get("/api/ps")
        loaded_response.raise_for_status()
        loaded = loaded_response.json()
        if not isinstance(loaded, dict) or not isinstance(loaded.get("models"), list):
            raise ValueError("Ollama /api/ps response must contain a models list")
        case["loaded_models"] = loaded["models"]
        for key in ["total_duration", "load_duration", "prompt_eval_count", "prompt_eval_duration", "eval_count", "eval_duration"]:
            if key in data:
                case[key] = data[key]
        case["passed"] = True
    except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError, AssertionError) as error:
        case["passed"] = False
        case["error"] = type(error).__name__
        if isinstance(error, (KeyError, IndexError, TypeError, ValueError, AssertionError)):
            case["detail"] = str(error)
        if isinstance(error, httpx.HTTPStatusError):
            case["http_status"] = error.response.status_code
            case["detail"] = error.response.text[:500]
    case["wall_seconds"] = round(time.perf_counter() - started, 3)
    return case


def main() -> None:
    """Print one safe JSON report and fail the command if any smoke case fails."""
    config = Settings.from_environment()
    report = {"python": platform.python_version(), "fastapi": fastapi.__version__, "cases": []}
    with GraphDatabase.driver(
        config.neo4j_uri,
        auth=(config.neo4j_user, config.neo4j_password.get_secret_value()),
        connection_timeout=5,
        max_transaction_retry_time=0,
    ) as driver:
        started = time.perf_counter()
        driver.verify_connectivity()
        records, _, _ = driver.execute_query("CALL dbms.components() YIELD versions, edition RETURN versions[0] AS version, edition")
        report["neo4j"] = dict(records[0])
        records, _, _ = driver.execute_query("RETURN gds.version() AS version")
        report["gds_version"] = records[0]["version"]
        records, _, _ = driver.execute_query("RETURN gds.isLicensed() AS licensed")
        report["gds_enterprise_licensed"] = records[0]["licensed"]
        records, _, _ = driver.execute_query("SHOW PROCEDURES YIELD name WHERE name IN $names RETURN name ORDER BY name", names=["gds.graph.list", "gds.graph.project", "gds.pageRank.stream", "gds.louvain.stream"])
        report["gds_procedures"] = [record["name"] for record in records]
        records, _, _ = driver.execute_query("CALL gds.graph.list() YIELD graphName RETURN graphName")
        report["gds_graph_list_count"] = len(records)
        report["bolt_gds_wall_seconds"] = round(time.perf_counter() - started, 3)

    with httpx.Client(base_url="http://127.0.0.1:8000", timeout=8, trust_env=False) as client:
        report["http"] = {}
        for path in ["/health/live", "/health/ready", "/docs", "/openapi.json"]:
            response = client.get(path)
            response.raise_for_status()
            report["http"][path] = response.status_code

    with httpx.Client(base_url=config.ollama_url, timeout=120, trust_env=False) as client:
        report["ollama_version"] = client.get("/api/version").json()["version"]
        report["models"] = client.get("/api/tags").json()["models"]
        options = {"num_ctx": 2048, "num_predict": 96, "temperature": 0, "seed": 42, "num_gpu": 0, "num_thread": 8}
        base = {"model": config.chat_model, "stream": False, "options": options, "keep_alive": "2m"}
        tools = [{"type": "function", "function": {
            "name": "lookup_paper", "description": "Look up a paper by its exact identifier.",
            "parameters": {"type": "object", "properties": {"paper_id": {"type": "string"}}, "required": ["paper_id"], "additionalProperties": False},
        }}]
        specs = [
            ("text", "/api/chat", {**base, "messages": [{"role": "user", "content": "Reply with one short sentence confirming that you can answer locally."}]}),
            ("structured_json", "/api/chat", {**base, "format": StructuredProbe.model_json_schema(), "messages": [{"role": "user", "content": 'Return project="GraphRAG" and local_only=true according to the supplied JSON schema.'}]}),
            ("tool_call", "/api/chat", {**base, "tools": tools, "messages": [{"role": "user", "content": "Use the lookup_paper tool to look up paper_id 2005.11401. Do not answer from memory."}]}),
            ("embedding", "/api/embed", {"model": config.embed_model, "input": ["search_query: What is graph retrieval?"], "keep_alive": "30s", "options": {"num_gpu": 0, "num_thread": 8}}),
        ]
        for name, path, payload in specs:
            report["cases"].append(run_ollama_case(client, name, path, payload))
        report["loaded_after_smoke"] = client.get("/api/ps").json()
    print(json.dumps(report, indent=2))
    if not all(case["passed"] for case in report["cases"]):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
