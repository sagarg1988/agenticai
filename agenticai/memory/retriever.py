"""
Long-term memory retriever — fetches relevant document chunks from Weaviate
using vector similarity search.

TODO: abstract behind a common VectorStoreRetriever interface so you can swap
      Weaviate for Pinecone / pgvector without changing callers.
"""

from __future__ import annotations

import logging
import os
from typing import Any

logger = logging.getLogger(__name__)

WEAVIATE_URL = os.environ.get("WEAVIATE_URL", "http://weaviate:8080")
DEFAULT_CLASS = "Document"
DEFAULT_LIMIT = 5


def _parse_weaviate_url(url: str) -> tuple[str, int]:
    url = url.replace("http://", "").replace("https://", "")
    parts = url.split(":")
    host = parts[0]
    port = int(parts[1]) if len(parts) > 1 else 8080
    return host, port


class MemoryRetriever:
    """Retrieves semantically similar chunks from Weaviate."""

    def __init__(self, class_name: str = DEFAULT_CLASS) -> None:
        import weaviate as _weaviate

        self.class_name = class_name
        host, port = _parse_weaviate_url(WEAVIATE_URL)
        # TODO: add authentication when Weaviate auth is enabled
        self._client = _weaviate.connect_to_local(host=host, port=port)

    def retrieve(self, query_embedding: list[float], limit: int = DEFAULT_LIMIT) -> list[dict[str, Any]]:
        """Return the top-k most similar documents to the query embedding."""
        logger.info("MemoryRetriever.retrieve", extra={"class": self.class_name, "limit": limit})
        collection = self._client.collections.get(self.class_name)
        results = collection.query.near_vector(near_vector=query_embedding, limit=limit)
        return [obj.properties for obj in results.objects]

    def close(self) -> None:
        self._client.close()
