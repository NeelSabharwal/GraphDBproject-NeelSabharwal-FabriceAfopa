"""Strict tool and response contracts; model output cannot supply query syntax."""

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, RootModel


class StrictModel(BaseModel):
    """Reject undeclared fields and coercion in untrusted model arguments."""

    model_config = ConfigDict(extra="forbid", strict=True, hide_input_in_errors=True)


class SearchChunks(StrictModel):
    """Semantic seeds, optionally restricted to an existing paper."""

    query: str = Field(min_length=1, max_length=1000)
    top_k: int = Field(default=4, ge=1, le=8)
    paper_id: str | None = Field(default=None, max_length=100)


class SourceExcerpt(StrictModel):
    """Fetch a complete authentic page-bounded chunk."""

    chunk_id: str = Field(min_length=1, max_length=100)


class CitationPath(StrictModel):
    """Directed path between two existing paper versions."""

    source_id: str = Field(min_length=1, max_length=100)
    target_id: str = Field(min_length=1, max_length=100)
    max_hops: int = Field(default=3, ge=1, le=3)


class ExpandEvidence(StrictModel):
    """One reviewed scientific relation hop, including shared-entity supports."""

    paper_id: str = Field(min_length=1, max_length=100)
    limit: int = Field(default=4, ge=1, le=8)


class ToolCall(StrictModel):
    """An untrusted request; the registry validates name and arguments separately."""

    name: str = Field(min_length=1, max_length=80)
    arguments: dict


class SearchAction(StrictModel):
    """Select bounded semantic retrieval through the approved search tool."""

    name: Literal["search_chunks"]
    arguments: SearchChunks


class ExcerptAction(StrictModel):
    """Select an explicit source read before using a Chunk as evidence."""

    name: Literal["get_source_excerpt"]
    arguments: SourceExcerpt


class PathAction(StrictModel):
    """Select a directed citation lookup with validated endpoint arguments."""

    name: Literal["find_citation_path"]
    arguments: CitationPath


class ExpandAction(StrictModel):
    """Select bounded expansion through student-approved scientific claims."""

    name: Literal["expand_verified_evidence"]
    arguments: ExpandEvidence


class EmptyArguments(StrictModel):
    """FINISH has no arguments or hidden executable content."""


class FinishAction(StrictModel):
    """Request completion; the workflow still enforces its evidence gate."""

    name: Literal["FINISH"]
    arguments: EmptyArguments


class NextAction(
    RootModel[
        Annotated[SearchAction | ExcerptAction | PathAction | ExpandAction | FinishAction, Field(discriminator="name")]
    ]
):
    """The same finite action schema constrains decoding and validates its result."""


class Statement(StrictModel):
    """Generated interpretation with one exact supporting source quotation."""

    text: str = Field(min_length=1, max_length=600)
    chunk_id: str = Field(min_length=1, max_length=100)
    quote: str = Field(min_length=8, max_length=600)


class Draft(StrictModel):
    """No model-supplied page, paper, status or claim identities are accepted."""

    statements: list[Statement] = Field(max_length=3)
    abstention: str = Field(max_length=400)


class PassageSelection(StrictModel):
    """The LLM selects source passages, not new factual sentences."""

    selected_ids: list[int] = Field(max_length=3)


class Evidence(StrictModel):
    """Source coordinates assigned by the database, never by the model."""

    chunk_id: str
    paper_id: str
    title: str
    page: int = Field(ge=1)
    text: str
    text_sha256: str
    pdf_sha256: str
    page_raw_sha256: str
    source_url: str
    source_version: str
    start_char: int
    end_char: int
    parser_version: str
    chunker_version: str
    status: Literal["SOURCE_LOCATED"] = "SOURCE_LOCATED"


class Citation(Evidence):
    """Validated exact quotation; offsets are relative to the normalized chunk."""

    quote: str
    quote_start: int
    quote_end: int


class TraceEvent(StrictModel):
    """Operational events only: no model thinking or hidden reasoning."""

    tool: str
    arguments: dict
    outcome: str
    duration_ms: float
    result: dict = Field(default_factory=dict)


class AskResponse(StrictModel):
    """A generated answer is not an approved graph assertion."""

    answer: str
    status: Literal["ANSWERED", "ABSTAINED", "REJECTED"]
    answer_status: Literal["HYPOTHESIS"] = "HYPOTHESIS"
    citations: list[Citation] = Field(default_factory=list)
    paths: list[dict] = Field(default_factory=list)
    trace: list[TraceEvent] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    latency_ms: float = 0
