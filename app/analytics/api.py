"""Validated graph GET endpoints; projection management has no HTTP route."""

from typing import Annotated, Literal
from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request
from neo4j.exceptions import Neo4jError, ServiceUnavailable
from pydantic import BaseModel, ConfigDict, Field

from app.analytics.gds import Analytics
from app.analytics.models import AnalyticsResponse, PathResponse, RelatedResponse, SharedResponse
from app.analytics.service import GraphUnavailable, UnknownPaper

router = APIRouter(prefix="/api/papers", tags=["Advanced graph"])
PAPER_PATTERN = r"^arxiv:\d{4}\.\d{4,5}v\d+$"
PaperID = Annotated[str, Path(pattern=PAPER_PATTERN, max_length=100)]


class Paging(BaseModel):
    model_config = ConfigDict(extra="forbid")
    limit: int = Field(default=20, ge=1, le=20)
    offset: int = Field(default=0, ge=0, le=100)


class PathOptions(BaseModel):
    model_config = ConfigDict(extra="forbid")
    target_id: str = Field(pattern=PAPER_PATTERN, max_length=100)
    max_hops: int = Field(default=3, ge=1, le=3)


class SharedOptions(Paging):
    target_id: str = Field(pattern=PAPER_PATTERN, max_length=100)
    kind: Literal["Method", "Dataset", "Task"] | None = None


def get_graph(request: Request):
    return Analytics(request.app.state.driver, request.app.state.settings)


async def guarded(awaitable):
    try:
        return await awaitable
    except UnknownPaper as error:
        raise HTTPException(404, detail=str(error)) from error
    except GraphUnavailable as error:
        raise HTTPException(503, detail=str(error)) from error
    except (Neo4jError, ServiceUnavailable, TimeoutError) as error:
        raise HTTPException(503, detail="Graph dependency or query budget unavailable") from error
    except ValueError as error:
        # Known argument errors only; other ValueErrors represent bad source/projection data.
        status = 400 if str(error).endswith("must be distinct") else 503
        raise HTTPException(
            status, detail="Endpoints must be distinct" if status == 400 else "Graph evidence validation failed"
        ) from error


async def run_algorithm(request, graph, algorithm, options):
    lock = request.app.state.analytics_lock
    if lock.locked():
        raise HTTPException(429, detail="Analytics busy; retry after the current request")
    async with lock:
        return await guarded(graph.run(algorithm, **options.model_dump()))


@router.get("/centrality", response_model=AnalyticsResponse)
async def centrality(request: Request, options: Annotated[Paging, Query()], graph=Depends(get_graph)):
    """Run real weighted GDS PageRank on the current prepared snapshot."""
    return await run_algorithm(request, graph, "pagerank", options)


@router.get("/communities", response_model=AnalyticsResponse)
async def communities(request: Request, options: Annotated[Paging, Query()], graph=Depends(get_graph)):
    """Run real weighted GDS Louvain; IDs are arbitrary, scope is the selected corpus."""
    return await run_algorithm(request, graph, "louvain", options)


@router.get("/{paper_id}/paths", response_model=PathResponse)
async def paths(paper_id: PaperID, options: Annotated[PathOptions, Query()], graph=Depends(get_graph)):
    """Find a bounded directed citation path and authenticate all source supports."""
    return await guarded(graph.path(paper_id, options.target_id, options.max_hops))


@router.get("/{paper_id}/shared", response_model=SharedResponse)
async def shared(paper_id: PaperID, options: Annotated[SharedOptions, Query()], graph=Depends(get_graph)):
    """Explore shared reviewed Method/Dataset/Task identities and both source claims."""
    return await guarded(graph.shared(paper_id, options.target_id, options.kind, options.limit, options.offset))


@router.get("/{paper_id}/related", response_model=RelatedResponse)
async def related(paper_id: PaperID, options: Annotated[Paging, Query()], graph=Depends(get_graph)):
    """Compare verified entity sets, sorted by Jaccard then ID, with bounded pagination."""
    return await guarded(graph.related(paper_id, options.limit, options.offset))
