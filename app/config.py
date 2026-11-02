"""Validated container configuration; secrets are never included in responses."""

import os

from pydantic import BaseModel, ConfigDict, Field, SecretStr


class Settings(BaseModel):
    """Local dependencies and hard upper bounds for agent resources."""

    model_config = ConfigDict(hide_input_in_errors=True)

    neo4j_uri: str = "bolt://neo4j:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: SecretStr = Field(min_length=16)
    ollama_url: str = "http://ollama:11434"
    chat_model: str = "qwen2.5:3b-instruct"
    embed_model: str = "nomic-embed-text:v1.5"
    readiness_timeout: float = Field(default=3, ge=0.1, le=10)
    agent_max_calls: int = Field(default=6, ge=1, le=8)
    agent_selection_retries: int = Field(default=1, ge=0, le=2)
    agent_timeout: float = Field(default=180, ge=1, le=300)
    agent_model_timeout: float = Field(default=45, ge=0.1, le=90)
    agent_query_timeout: float = Field(default=5, ge=0.1, le=10)
    agent_context_chars: int = Field(default=6500, ge=500, le=9000)
    corpus_import_token: SecretStr | None = Field(default=None, min_length=32)
    corpus_root: str = "/workspace"

    @classmethod
    def from_environment(cls) -> "Settings":
        """Read environment without loading or printing a dotenv file."""
        return cls(
            neo4j_uri=os.getenv("NEO4J_URI", "bolt://neo4j:7687"),
            neo4j_user=os.getenv("NEO4J_USER", "neo4j"),
            neo4j_password=os.environ["NEO4J_PASSWORD"],
            ollama_url=os.getenv("OLLAMA_URL", "http://ollama:11434"),
            chat_model=os.getenv("OLLAMA_CHAT_MODEL", "qwen2.5:3b-instruct"),
            embed_model=os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text:v1.5"),
            readiness_timeout=os.getenv("READINESS_TIMEOUT", "3"),
            agent_max_calls=os.getenv("AGENT_MAX_CALLS", "6"),
            agent_selection_retries=os.getenv("AGENT_SELECTION_RETRIES", "1"),
            agent_timeout=os.getenv("AGENT_TIMEOUT", "180"),
            agent_model_timeout=os.getenv("AGENT_MODEL_TIMEOUT", "45"),
            agent_query_timeout=os.getenv("AGENT_QUERY_TIMEOUT", "5"),
            agent_context_chars=os.getenv("AGENT_CONTEXT_CHARS", "6500"),
            corpus_import_token=os.getenv("CORPUS_IMPORT_TOKEN") or None,
            corpus_root=os.getenv("CORPUS_ROOT", "/workspace"),
        )
