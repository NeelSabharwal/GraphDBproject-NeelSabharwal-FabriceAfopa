"""Typed analytical responses; scores remain derived results, not reviewed facts."""

from typing import Literal
from pydantic import BaseModel, ConfigDict, Field
from app.agent.models import Evidence


class Model(BaseModel):
    """Reject extra analytical fields and nonfinite numeric results."""

    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)


class Support(BaseModel):
    """Existing retrieval provenance plus optional scientific qualifications."""

    model_config = ConfigDict(extra="allow", allow_inf_nan=False)
    claim_id: str
    predicate: Literal["CITES", "USES", "EVALUATED_ON", "ADDRESSES"]
    subject_id: str
    object_id: str
    chunk_id: str
    quote: str
    start_char: int = Field(ge=0)
    end_char: int = Field(gt=0)
    quote_sha256: str
    status: Literal["SOURCE_VERIFIED"]


class CitationEdge(Model):
    """A directed citation edge with the reviewed claims supporting it."""

    source: str
    target: str
    claims: list[Support]


class CitationRoute(Model):
    """An ordered Paper path and the source-supported edges connecting it."""

    type: Literal["CITES"]
    papers: list[str]
    edges: list[CitationEdge]


class PathResponse(Model):
    """Return authenticated citation paths or an explicit unavailable result."""

    status: Literal["ok", "unavailable"]
    paths: list[CitationRoute]
    evidence: list[Evidence]
    limitation: str | None = None


class SharedEntity(Model):
    """A scoped scientific identity with claim IDs from both compared Papers."""

    entity_id: str
    name: str
    kind: Literal["Method", "Dataset", "Task"]
    source_claim_ids: list[str]
    target_claim_ids: list[str]


class SharedResponse(Model):
    """A page of shared identities with complete claim and Chunk evidence."""

    source: str
    target: str
    entities: list[SharedEntity]
    supports: list[Support]
    evidence: list[Evidence]
    offset: int = Field(ge=0)
    limit: int = Field(ge=1, le=20)


class RelatedPaper(Model):
    """A Paper ranked by scoped entity overlap, not scientific quality."""

    paper_id: str
    title: str
    similarity: float = Field(gt=0, le=1)
    entity_ids: list[str]
    source_claim_ids: list[str]
    target_claim_ids: list[str]


class RelatedResponse(Model):
    """Paginated similarity results with source support and interpretation limits."""

    source: str
    papers: list[RelatedPaper]
    supports: list[Support]
    evidence: list[Evidence]
    offset: int = Field(ge=0)
    limit: int = Field(ge=1, le=20)
    interpretation: str


class Rank(Model):
    """A streamed PageRank score and its validated weighted degree."""

    paper_id: str
    title: str
    score: float = Field(ge=0)
    weighted_degree: float = Field(ge=0)


class Membership(Model):
    """A streamed community assignment; numeric community IDs are arbitrary."""

    paper_id: str
    title: str
    community_id: int = Field(ge=0)
    community_size: int = Field(ge=1)


class Adjacency(Model):
    """A derived Jaccard edge with the reviewed claims behind its entity sets."""

    source: str
    target: str
    shared: list[str]
    union_size: int = Field(gt=0)
    weight: float = Field(gt=0, le=1)
    source_claim_ids: list[str]
    target_claim_ids: list[str]


class AnalyticsResponse(Model):
    """Expose snapshot, projection, budgets and streamed GDS results together."""

    algorithm: Literal["pagerank", "louvain"]
    projection: str
    snapshot: str
    node_count: int = Field(ge=1, le=16)
    logical_edge_count: int = Field(ge=0, le=120)
    projected_relationship_count: int = Field(ge=0, le=240)
    isolated_papers: list[str]
    adjacencies: list[Adjacency]
    configuration: dict
    memory_estimate: dict
    stats: dict
    stream_millis: float = Field(ge=0)
    elapsed_millis: float = Field(ge=0)
    ranks: list[Rank] = Field(default_factory=list)
    memberships: list[Membership] = Field(default_factory=list)
    stream_modularity: float | None = None
    offset: int = Field(ge=0)
    limit: int = Field(ge=1, le=20)
    interpretation: str
