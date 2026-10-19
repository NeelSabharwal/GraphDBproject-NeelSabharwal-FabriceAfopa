"""Bounded dependency probes; no inference or graph mutations on health checks."""

import asyncio
from typing import Literal

from fastapi import Request
from neo4j import Query
from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Public health result deliberately excludes exception details and secrets."""

    status: Literal["ok", "ready", "not_ready"]
    checks: dict[str, Literal["ok", "unavailable", "models_missing"]] = {}


async def check_neo4j(request: Request) -> str:
    """Verify authenticated Bolt and an actual GDS function within a deadline."""
    timeout = request.app.state.settings.readiness_timeout
    try:
        async with asyncio.timeout(timeout):
            async with request.app.state.driver.session(default_access_mode="READ") as session:
                result = await session.run(Query("RETURN gds.version() AS version", timeout=timeout))
                record = await result.single(strict=True)
                return "ok" if record["version"] == "2.13.2" else "unavailable"
    except Exception:  # Dependency errors must become a safe 503, never leak configuration.
        return "unavailable"


async def check_ollama(request: Request) -> str:
    """Check the server and exact required model tags without loading weights."""
    settings = request.app.state.settings
    try:
        async with asyncio.timeout(settings.readiness_timeout):
            response = await request.app.state.http.get("/api/tags")
            response.raise_for_status()
            names = {item["name"] for item in response.json()["models"]}
            return "ok" if {settings.chat_model, settings.embed_model} <= names else "models_missing"
    except Exception:
        return "unavailable"


async def check_readiness(request: Request) -> HealthResponse:
    """Run independent probes concurrently, bounded by one probe deadline."""
    neo4j_status, ollama_status = await asyncio.gather(check_neo4j(request), check_ollama(request))
    checks = {"neo4j_gds": neo4j_status, "ollama": ollama_status}
    return HealthResponse(status="ready" if all(v == "ok" for v in checks.values()) else "not_ready", checks=checks)
