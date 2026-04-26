"""
Embedding provider — generates dense vector embeddings for text.

TODO:
- Support multiple embedding backends (OpenAI, Cohere, local sentence-transformers)
  switchable via EMBEDDING_BACKEND env var.
- Cache embeddings to avoid redundant API calls.
- Batch embed large document sets.
"""
from __future__ import annotations

import logging
from typing import Any

from django.conf import settings

logger = logging.getLogger(__name__)


class EmbeddingProvider:
    """
    Generates embeddings for text using the configured backend.

    Supported backends:
    - "sentence_transformers" (default, local, no API key required)
    - "openai" (requires OPENAI_API_KEY)

    TODO: add "cohere" and "vertex" backends.
    """

    def __init__(self, backend: str | None = None) -> None:
        self.backend = backend or getattr(settings, "EMBEDDING_BACKEND", "sentence_transformers")
        self._model = None  # lazy-initialised

    def _load_model(self) -> Any:
        if self._model is None:
            if self.backend == "sentence_transformers":
                from sentence_transformers import SentenceTransformer  # noqa: PLC0415

                # TODO: make model name configurable via settings
                self._model = SentenceTransformer("all-MiniLM-L6-v2")
            elif self.backend == "openai":
                # TODO: initialise openai client with key from secrets manager
                import openai  # noqa: PLC0415

                self._model = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
            else:
                raise ValueError(f"Unknown embedding backend: {self.backend!r}")
        return self._model

    def embed(self, text: str) -> list[float]:
        """Return a dense embedding vector for *text*."""
        model = self._load_model()
        if self.backend == "sentence_transformers":
            vector = model.encode(text, normalize_embeddings=True)
            return vector.tolist()
        elif self.backend == "openai":
            response = model.embeddings.create(
                model="text-embedding-3-small",
                input=text,
            )
            return response.data[0].embedding
        raise NotImplementedError(f"embed() not implemented for backend '{self.backend}'")

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Return embeddings for a batch of texts."""
        return [self.embed(t) for t in texts]
