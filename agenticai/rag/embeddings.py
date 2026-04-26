"""
Embedding provider — wraps OpenAI Embeddings API.

TODO: abstract behind an EmbeddingProvider interface to support:
  - OpenAI text-embedding-3-small/large
  - HuggingFace sentence-transformers (local, no API key needed)
  - Azure OpenAI Embeddings
"""

from __future__ import annotations

import logging
import os

logger = logging.getLogger(__name__)

DEFAULT_MODEL = os.environ.get("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")


class EmbeddingProvider:
    """Generates vector embeddings for text using OpenAI."""

    def __init__(self, model: str = DEFAULT_MODEL) -> None:
        from openai import OpenAI  # noqa: PLC0415

        # TODO: validate that OPENAI_API_KEY is set; raise a clear error if not
        self._client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""))
        self.model = model

    def embed(self, text: str) -> list[float]:
        logger.debug("EmbeddingProvider.embed", extra={"model": self.model, "text_len": len(text)})
        response = self._client.embeddings.create(input=[text], model=self.model)
        return response.data[0].embedding

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        logger.debug("EmbeddingProvider.embed_batch", extra={"model": self.model, "count": len(texts)})
        response = self._client.embeddings.create(input=texts, model=self.model)
        return [item.embedding for item in response.data]
