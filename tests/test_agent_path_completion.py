"""A real returned path must lead to complete source reads, never repeated lookup loops."""

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app.agent.models import ToolCall, TraceEvent
from app.agent.workflow import EvidenceAgent, action_schema
from app.config import Settings
from app.ingestion.documents import digest


def fixture():
    sources = []
    for i in range(3):
        text = f"Synthetic bibliography source number {i} supporting a fixture citation."
        if i == 1:
            text += " Unrelated surrounding context must not outrank the marked citation excerpt." * 2
        sources.append(
            dict(
                chunk_id=f"c{i}",
                paper_id=f"p{i}",
                title="Synthetic",
                page=1,
                text=text,
                text_sha256=digest(text),
                pdf_sha256="fixture",
                page_raw_sha256="fixture",
                source_url="https://example.invalid",
                source_version="v1",
                start_char=0,
                end_char=len(text),
                parser_version="fixture",
                chunker_version="fixture",
                status="SOURCE_LOCATED",
            )
        )
    supports = [
        dict(chunk_id=s["chunk_id"], quote=s["text"], support_role="context" if i == 1 else "excerpt")
        for i, s in enumerate(sources)
    ]
    path = dict(
        type="CITES",
        papers=["p0", "p1", "p2"],
        edges=[
            dict(source="p0", target="p1", claims=supports[:2]),
            dict(source="p1", target="p2", claims=supports[2:]),
        ],
    )
    return sources, path


@pytest.mark.parametrize("budget,expected", [(4, "ANSWERED"), (3, "ABSTAINED")])
def test_path_reads_all_support_chunks_before_answering(budget, expected):
    sources, path = fixture()

    async def exercise():
        model = SimpleNamespace(
            select=AsyncMock(
                side_effect=[
                    ToolCall(name="find_citation_path", arguments=dict(source_id="p0", target_id="p2")),
                    *[ToolCall(name="get_source_excerpt", arguments=dict(chunk_id=s["chunk_id"])) for s in sources],
                ]
            ),
            answer=AsyncMock(),
        )
        tools = SimpleNamespace(
            catalog=AsyncMock(return_value=[dict(id=f"p{i}", title=f"Paper {i}", aliases=[]) for i in range(3)]),
            execute=AsyncMock(
                side_effect=[
                    dict(status="ok", paths=[path], evidence=sources),
                    *[dict(status="ok", evidence=[s]) for s in sources],
                ]
            ),
        )
        result = await EvidenceAgent(
            tools, model, Settings(neo4j_password="synthetic-password-only", agent_max_calls=budget)
        ).ask("Give a citation chain")
        assert result.status == expected
        assert sum(e.tool == "find_citation_path" for e in result.trace) == 1
        assert result.paths == [path]
        if expected == "ANSWERED":
            assert len(result.citations) == 2
            assert [c.chunk_id for c in result.citations] == ["c0", "c2"]
            assert all(c.status == "SOURCE_LOCATED" for c in result.citations)
        model.answer.assert_not_awaited()

    asyncio.run(exercise())


def test_path_schema_forbids_repeated_lookup_and_premature_finish():
    sources, path = fixture()
    state = dict(
        question="Give a citation chain",
        evidence={s["chunk_id"]: s for s in sources},
        read_ids=["c0", "c1"],
        paths=[path],
        trace=[TraceEvent(tool="find_citation_path", arguments={}, outcome="ok", duration_ms=1)],
    )
    schema, allowed, chunks, _ = action_schema(state)
    assert allowed == {"get_source_excerpt": "ExcerptAction"}
    assert chunks == ["c2"]
    assert schema["$defs"]["SourceExcerpt"]["properties"]["chunk_id"]["enum"] == ["c2"]
    state["read_ids"].append("c2")
    assert action_schema(state)[1] == {"FINISH": "FinishAction"}
