"""Authenticated pinned import and bounded read-only corpus/exploration endpoints."""

import asyncio
import secrets
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, ConfigDict, Field

from app.agent.models import Evidence
from app.analytics.api import guarded
from app.analytics.models import Support
from app.corpus.service import CorpusConflict, CorpusService, import_corpus

router = APIRouter(prefix="/api", tags=["Corpus"])
bearer = HTTPBearer(auto_error=False)


class ImportOptions(BaseModel):
    """Only the pinned prototype; no client-controlled filesystem path or URL."""

    model_config = ConfigDict(extra="forbid")
    corpus: Literal["prototype-v1"] = "prototype-v1"
    sample_per_paper: int = Field(default=0, ge=0, le=1, strict=True)


class ConceptNode(BaseModel):
    """Expose a graph identity and display name without private node properties."""

    id: str
    label: Literal["Entity", "Claim", "Paper"]
    name: str


class ConceptEdge(BaseModel):
    """Preserve an actual directed SUBJECT or OBJECT relationship."""

    source: str
    target: str
    type: Literal["OBJECT", "SUBJECT"]


class ConceptGraph(BaseModel):
    """Return bounded concept exploration with reviewed supports and source Chunks."""

    entity_id: str
    depth: int = Field(ge=1, le=2)
    nodes: list[ConceptNode]
    edges: list[ConceptEdge]
    supports: list[Support]
    evidence: list[Evidence]


def get_corpus(request: Request):
    """Dependency seam for API behavior tests, without touching live containers."""
    return CorpusService(request.app.state.driver, request.app.state.settings)


def authorize_import(request: Request, credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)]):
    """Fail closed and compare a high-entropy environment-supplied bearer token."""
    token = request.app.state.settings.corpus_import_token
    if token is None:
        raise HTTPException(503, detail="Corpus import is disabled until an operator configures authentication")
    if credentials is None:
        raise HTTPException(401, detail="Bearer authentication required", headers={"WWW-Authenticate": "Bearer"})
    if not secrets.compare_digest(credentials.credentials.encode(), token.get_secret_value().encode()):
        raise HTTPException(403, detail="Invalid import credential")


@router.get("/corpus")
async def catalog(graph=Depends(get_corpus)):
    """Discover real paper IDs for subsequent graph requests."""
    return {"papers": await guarded(graph.catalog())}


@router.post("/corpus/import", dependencies=[Depends(authorize_import)])
async def import_pinned(options: ImportOptions, request: Request):
    """Import the fixed public corpus, without granting any scientific approval."""
    lock = request.app.state.import_lock
    if lock.locked():
        raise HTTPException(409, detail="An import is already running")
    async with lock:
        try:
            result = await guarded(
                asyncio.to_thread(import_corpus, request.app.state.settings, options.sample_per_paper)
            )
        except CorpusConflict as error:
            raise HTTPException(409, detail=str(error)) from error
    if result["status"] == "FAILED":
        raise HTTPException(503, detail=result)
    return result


@router.get("/topics/{ident}/graph", response_model=ConceptGraph)
async def topic(
    ident: Annotated[str, Path(min_length=1, max_length=160, pattern=r"^[A-Za-z0-9:._-]+$")],
    depth: Annotated[int, Query(ge=1, le=2)] = 2,
    graph=Depends(get_corpus),
):
    """Return actual directed relationships and complete reviewed source supports."""
    return await guarded(graph.topic(ident, depth))
