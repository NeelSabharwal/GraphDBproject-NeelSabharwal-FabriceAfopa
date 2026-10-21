"""Direct local Ollama interfaces with pinned embedding identity and validation."""

import math
import json

from app.agent.models import Draft, NextAction, PassageSelection, ToolCall
from app.agent.grounding import candidates, extractive_draft

EMBED_MODEL = "nomic-embed-text:v1.5"
EMBED_DIGEST = "0a109f422b47e3a30ba2b10eca18548e944e8a23073ee3f3e947efcf3c45e59f"
DIMENSIONS = 768
EMBED_POLICY = "nomic-search-prefix-v1"
INDEX = "chunk_nomic_v1"


class Ollama:
    """Reuse the app's HTTP client; each request has its own inference timeout."""

    def __init__(self, client, settings):
        self.client = client
        self.settings = settings

    async def identity(self):
        """Refuse a mutable tag that no longer resolves to the pinned weights."""
        response = await self.client.get("/api/tags", timeout=5)
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict) or not isinstance(payload.get("models"), list):
            raise ValueError("Invalid Ollama model registry")
        if not any(isinstance(m, dict) and m.get("name") == EMBED_MODEL
                   and m.get("digest") == EMBED_DIGEST for m in payload["models"]):
            raise ValueError("Pinned embedding model/digest unavailable")

    async def embed(self, texts, *, query=False):
        """Nomic requires distinct search_query/search_document prefixes."""
        await self.identity()
        prefix = "search_query: " if query else "search_document: "
        response = await self.client.post("/api/embed", json={
            "model": EMBED_MODEL, "input": [prefix + text for text in texts],
            "truncate": False, "keep_alive": "2m",
        }, timeout=self.settings.agent_model_timeout)
        response.raise_for_status()
        payload = response.json()
        vectors = payload.get("embeddings") if isinstance(payload, dict) else None
        if not isinstance(vectors, list) or len(vectors) != len(texts):
            raise ValueError("Embedding response count mismatch")
        for vector in vectors:
            if (not isinstance(vector, list) or len(vector) != DIMENSIONS
                    or any(type(x) not in (int, float) or not math.isfinite(x) for x in vector)
                    or sum(x * x for x in vector) == 0):
                raise ValueError("Invalid embedding dimensions or numeric values")
        return vectors

    async def chat(self, messages, *, max_tokens=500, **kwargs):
        """Bound generation; reject truncated or unexpected response payloads."""
        response = await self.client.post("/api/chat", json={
            "model": self.settings.chat_model, "stream": False, "messages": messages,
            "options": {"temperature": 0, "seed": 42, "num_predict": max_tokens,
                        "num_ctx": 4096, "num_thread": 8},
            **kwargs,
        }, timeout=self.settings.agent_model_timeout)
        response.raise_for_status()
        payload = response.json()
        if (not isinstance(payload, dict) or payload.get("done") is not True
                or payload.get("done_reason") == "length"
                or not isinstance(payload.get("message"), dict)):
            raise ValueError("Invalid or truncated Ollama chat response")
        return payload["message"]

    async def select(self, messages, schema):
        """Constrain local decoding, then independently validate names and arguments."""
        message = await self.chat(messages, format=schema, max_tokens=240)
        content = message.get("content")
        if not isinstance(content, str):
            raise ValueError("Selection content must be a JSON string")
        try:
            action = NextAction.model_validate_json(content).root
        except ValueError as error:
            raise ValueError("Selection failed the next-action JSON schema") from error
        return ToolCall(name=action.name, arguments=action.arguments.model_dump())

    async def answer(self, messages, *, evidence, question):
        """One small selection pass; statements are source text, not unsupported paraphrases."""
        options = candidates(question, evidence)
        if not options:
            return Draft(statements=[], abstention="No sufficiently relevant source passages found.")
        schema = PassageSelection.model_json_schema()
        schema["properties"]["selected_ids"]["items"]["enum"] = [o["id"] for o in options]
        message = await self.chat(messages + [{"role": "user", "content":
            "UNTRUSTED SOURCE PASSAGES:\n" + json.dumps(options)}], format=schema, max_tokens=80)
        selection = PassageSelection.model_validate_json(message.get("content", ""))
        return extractive_draft(selection.selected_ids, options, question)
