"""
RAG document ingestor — chunks, embeds, and upserts documents into Weaviate.

TODO: support incremental ingestion (skip already-indexed documents by hash).
TODO: add support for PDF, DOCX, HTML source types via LangChain document loaders.
"""

from __future__ import annotations

import logging
import os
import uuid
from typing import Any

logger = logging.getLogger(__name__)

WEAVIATE_URL = os.environ.get("WEAVIATE_URL", "http://weaviate:8080")
COLLECTION_NAME = "Document"
CHUNK_SIZE = 500  # characters per chunk
CHUNK_OVERLAP = 50


def _chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + size, len(text))
        chunks.append(text[start:end])
        start += size - overlap
    return chunks


class DocumentIngestor:
    """Chunks text, generates embeddings, and upserts into Weaviate."""

    def __init__(self) -> None:
        import weaviate
        from weaviate.classes.config import Configure, Property, DataType

        self._Configure = Configure
        self._Property = Property
        self._DataType = DataType

        host, port = _parse_weaviate_url(WEAVIATE_URL)
        self._client = weaviate.connect_to_local(host=host, port=port)

        from agenticai.rag.embeddings import EmbeddingProvider  # noqa: PLC0415

        self._embedder = EmbeddingProvider()
        self._ensure_collection()

    def _ensure_collection(self) -> None:
        """Create the Document collection if it doesn't exist."""
        if not self._client.collections.exists(COLLECTION_NAME):
            self._client.collections.create(
                name=COLLECTION_NAME,
                # TODO: configure vectorizer to use Weaviate's built-in module instead of manual vectors
                vectorizer_config=self._Configure.Vectorizer.none(),
                properties=[
                    self._Property(name="text", data_type=self._DataType.TEXT),
                    self._Property(name="source", data_type=self._DataType.TEXT),
                    self._Property(name="chunk_index", data_type=self._DataType.INT),
                ],
            )
            logger.info("DocumentIngestor: created Weaviate collection", extra={"name": COLLECTION_NAME})

    def ingest(self, text: str, source: str = "unknown") -> int:
        """Ingest a document, returning the number of chunks written."""
        chunks = _chunk_text(text)
        embeddings = self._embedder.embed_batch(chunks)
        collection = self._client.collections.get(COLLECTION_NAME)

        objects: list[dict[str, Any]] = []
        for idx, (chunk, vector) in enumerate(zip(chunks, embeddings)):
            objects.append(
                {
                    "uuid": str(uuid.uuid4()),
                    "properties": {"text": chunk, "source": source, "chunk_index": idx},
                    "vector": vector,
                }
            )

        collection.data.insert_many(objects)
        logger.info("DocumentIngestor.ingest", extra={"source": source, "chunks": len(chunks)})
        return len(chunks)

    def close(self) -> None:
        self._client.close()


def _parse_weaviate_url(url: str) -> tuple[str, int]:
    url = url.replace("http://", "").replace("https://", "")
    parts = url.split(":")
    host = parts[0]
    port = int(parts[1]) if len(parts) > 1 else 8080
    return host, port
