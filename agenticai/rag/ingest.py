"""
RAG Ingest — chunks documents and upserts embeddings into the vector store.

TODO:
- Add support for PDF, HTML, and DOCX document loaders.
- Use overlapping chunks for better retrieval quality.
- Track ingestion metadata (source URL, ingested_at) in the vector store.
- Abstract vector DB backend behind a common interface.
"""
from __future__ import annotations

import logging
from typing import Any

from django.conf import settings

from rag.embeddings import EmbeddingProvider

logger = logging.getLogger(__name__)

_DEFAULT_CHUNK_SIZE = 512
_DEFAULT_CHUNK_OVERLAP = 64


def _chunk_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    """Split *text* into overlapping chunks of approximately *chunk_size* chars."""
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks


class DocumentIngestor:
    """
    Ingests plain-text documents into the vector store.

    Args:
        collection_name: Weaviate collection to upsert into.
        chunk_size: Approximate character length of each chunk.
        overlap: Overlap between consecutive chunks.
    """

    def __init__(
        self,
        collection_name: str = "Documents",
        chunk_size: int = _DEFAULT_CHUNK_SIZE,
        overlap: int = _DEFAULT_CHUNK_OVERLAP,
    ) -> None:
        self.collection_name = collection_name
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.embedder = EmbeddingProvider()
        self._weaviate_client = None  # lazy-initialised

    def _get_client(self):
        if self._weaviate_client is None:
            try:
                import weaviate  # noqa: PLC0415

                self._weaviate_client = weaviate.connect_to_local(
                    host=settings.WEAVIATE_URL.replace("http://", "").split(":")[0],
                    port=int(settings.WEAVIATE_URL.split(":")[-1]),
                )
            except Exception as exc:  # noqa: BLE001
                logger.error("Failed to connect to Weaviate: %s", exc)
                raise
        return self._weaviate_client

    def ingest(self, text: str, metadata: dict[str, Any] | None = None) -> int:
        """
        Chunk *text*, embed each chunk, and upsert into the vector store.

        Returns:
            Number of chunks ingested.
        """
        chunks = _chunk_text(text, self.chunk_size, self.overlap)
        logger.info(
            "Ingesting %d chunks into collection '%s'", len(chunks), self.collection_name
        )
        for chunk in chunks:
            vector = self.embedder.embed(chunk)
            # TODO: upsert chunk + vector + metadata into Weaviate
            # client = self._get_client()
            # client.collections.get(self.collection_name).data.insert(
            #     properties={"text": chunk, **(metadata or {})},
            #     vector=vector,
            # )
            _ = vector  # placeholder until Weaviate client is wired up
        return len(chunks)
