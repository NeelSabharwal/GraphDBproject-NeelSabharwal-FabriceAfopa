"""Minimal FastAPI lifecycle, Swagger and truthful health endpoints."""

from contextlib import asynccontextmanager

import httpx
from fastapi import Depends, FastAPI, Response
from neo4j import AsyncGraphDatabase

from app.config import Settings
from app.health import HealthResponse, check_readiness


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create isolated clients for the app lifespan; connect only during probes."""

    @asynccontextmanager
    async def lifespan(application: FastAPI):
        config = settings or Settings.from_environment()
        application.state.settings = config
        async with AsyncGraphDatabase.driver(
            config.neo4j_uri,
            auth=(config.neo4j_user, config.neo4j_password.get_secret_value()),
            connection_timeout=config.readiness_timeout,
            connection_acquisition_timeout=config.readiness_timeout,
            max_transaction_retry_time=0,
            max_connection_pool_size=4,
        ) as driver, httpx.AsyncClient(
            base_url=config.ollama_url,
            timeout=config.readiness_timeout,
            trust_env=False,
        ) as client:
            application.state.driver = driver
            application.state.http = client
            yield

    application = FastAPI(title="AI Research GraphRAG Assistant", version="0.1.0", lifespan=lifespan)

    @application.get("/health/live", response_model=HealthResponse)
    async def live() -> HealthResponse:
        """Report process liveness independently of external dependencies."""
        return HealthResponse(status="ok")

    @application.get("/health/ready", response_model=HealthResponse, responses={503: {"model": HealthResponse}})
    async def ready(response: Response, health: HealthResponse = Depends(check_readiness)) -> HealthResponse:
        """Return 503 until Bolt/GDS, Ollama and both required model tags work."""
        if health.status != "ready":
            response.status_code = 503
        return health

    return application


app = create_app()
