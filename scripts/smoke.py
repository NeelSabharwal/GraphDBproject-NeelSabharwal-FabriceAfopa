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
            started = time.perf_counter()
            case = {"name": name}
            try:
                response = client.post(path, json=payload)
                response.raise_for_status()
                data = response.json()
                if name == "text":
                    content = data["message"]["content"]
                    assert content.strip(), "Empty text response"
                    case["output"] = content
                elif name == "structured_json":
                    output = StructuredProbe.model_validate_json(data["message"]["content"])
                    assert output.project == "GraphRAG" and output.local_only is True
                    case["output"] = output.model_dump()
                elif name == "tool_call":
                    calls = data["message"].get("tool_calls", [])
                    assert len(calls) == 1, "Expected exactly one actual tool call"
                    function = calls[0]["function"]
                    assert function["name"] == "lookup_paper"
                    assert function["arguments"] == {"paper_id": "2005.11401"}
                    case["output"] = calls
                    case["note"] = "Tool selection/arguments only; no graph lookup or agent implemented."
                else:
                    vector = data["embeddings"][0]
                    assert len(vector) == 768 and all(math.isfinite(v) for v in vector)
                    norm = math.sqrt(sum(v*v for v in vector))
                    assert norm > 0
                    case["output"] = {"vectors": len(data["embeddings"]), "dimensions": len(vector), "l2_norm": round(norm, 6)}
                case["passed"] = True
                case["loaded_models"] = client.get("/api/ps").json()["models"]
                for key in ["total_duration", "load_duration", "prompt_eval_count", "prompt_eval_duration", "eval_count", "eval_duration"]:
                    if key in data:
                        case[key] = data[key]
            except (httpx.HTTPError, KeyError, ValueError, AssertionError) as error:
                case["passed"] = False
                case["error"] = type(error).__name__
                if isinstance(error, AssertionError):
                    case["detail"] = str(error)
                if isinstance(error, httpx.HTTPStatusError):
                    case["http_status"] = error.response.status_code
                    case["detail"] = error.response.text[:500]
            case["wall_seconds"] = round(time.perf_counter() - started, 3)
            report["cases"].append(case)
        report["loaded_after_smoke"] = client.get("/api/ps").json()
    print(json.dumps(report, indent=2))
    if not all(case["passed"] for case in report["cases"]):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
