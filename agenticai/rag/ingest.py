import uuid
from urllib.parse import urlparse

import weaviate
import weaviate.classes as wvc
from django.conf import settings

from .embeddings import EmbeddingProvider


def _connect():
    parsed = urlparse(settings.WEAVIATE_URL)
    host = parsed.hostname or "weaviate"
    port = parsed.port or 8080
    secure = parsed.scheme == "https"
    return weaviate.connect_to_custom(
        http_host=host,
        http_port=port,
        http_secure=secure,
        grpc_host=host,
        grpc_port=50051,
        grpc_secure=False,
        skip_init_checks=True,
    )


def chunk_text(text, chunk_size=1000, overlap=200):
    tokens = text.split()
    chunks = []
    i = 0
    while i < len(tokens):
        chunk = tokens[i:i+chunk_size]
        chunks.append(" ".join(chunk))
        i += (chunk_size - overlap)
    return chunks


def ingest_document(title, text, metadata):
    emb = EmbeddingProvider()
    cls = "Memory"
    chunks = chunk_text(text)
    with _connect() as client:
        # Ensure the collection exists (skip creation if already present)
        if not client.collections.exists(cls):
            client.collections.create(
                name=cls,
                vectorizer_config=wvc.config.Configure.Vectorizer.none(),
            )
        collection = client.collections.get(cls)
        for i, chunk in enumerate(chunks):
            vec = emb.embed_text(chunk)
            obj = {"text": chunk, "metadata": {"title": title, **metadata, "chunk_index": i}}
            collection.data.insert(properties=obj, vector=vec, uuid=str(uuid.uuid4()))
    return {"status": "ok", "chunks": len(chunks)}
