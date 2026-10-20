"""Validated container configuration; secrets are never included in responses."""

import os

from pydantic import BaseModel, ConfigDict, Field, SecretStr


class Settings(BaseModel):
    """Only configuration needed for the infrastructure milestone."""

    model_config = ConfigDict(hide_input_in_errors=True)

    neo4j_uri: str = "bolt://neo4j:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: SecretStr = Field(min_length=16)
    ollama_url: str = "http://ollama:11434"
    chat_model: str = "qwen2.5:3b-instruct"
    embed_model: str = "nomic-embed-text:v1.5"
    readiness_timeout: float = Field(default=3, ge=0.1, le=10)

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
        )
