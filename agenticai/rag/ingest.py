import uuid

import weaviate.classes as wvc
from django.conf import settings

from .embeddings import EmbeddingProvider
from .weaviate_client import get_weaviate_client


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
    with get_weaviate_client() as client:
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
