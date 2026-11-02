"""One local ask endpoint; dependency overrides keep tests deterministic."""

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from neo4j.exceptions import Neo4jError, ServiceUnavailable, SessionExpired

from app.agent.models import AskResponse
from app.agent.ollama import Ollama
from app.agent.tools import RetrievalTools
from app.agent.workflow import AgentTimeout, EvidenceAgent

router = APIRouter()


def get_agent(request: Request):
    """Use existing async clients; no DB or inference calls during construction."""
    state = request.app.state
    model = Ollama(state.http, state.settings)
    return EvidenceAgent(RetrievalTools(state.driver, model, state.settings), model, state.settings)


@router.get("/api/ask", response_model=AskResponse)
async def ask(
    request: Request, q: str = Query(min_length=1, max_length=1000), agent: EvidenceAgent = Depends(get_agent)
):
    """Return source-grounded generation or an explicit bounded failure/abstention."""
    if not q.strip():
        raise HTTPException(422, detail="Question must not be blank")
    # One CPU inference workflow at a time; reject contention rather than queue forever.
    lock = request.app.state.agent_lock
    if lock.locked():
        raise HTTPException(429, detail="Agent busy; retry after the current request")
    async with lock:
        try:
            return await agent.ask(q)
        except AgentTimeout as error:
            return JSONResponse(status_code=504, content=error.response.model_dump())
        except (TimeoutError, httpx.TimeoutException) as error:
            raise HTTPException(504, detail="Agent dependency or request deadline exceeded") from error
        except (httpx.HTTPError, Neo4jError, ServiceUnavailable, SessionExpired) as error:
            raise HTTPException(503, detail="Retrieval or local inference dependency unavailable") from error
        except ValueError as error:
            raise HTTPException(503, detail="Retrieval configuration or source validation failed") from error
