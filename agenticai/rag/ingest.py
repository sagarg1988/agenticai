import uuid
from .embeddings import EmbeddingProvider
import weaviate
from django.conf import settings

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
    client = weaviate.Client(url=settings.WEAVIATE_URL)
    cls = "Memory"
    # create class if needed (skip robust checks for brevity)
    chunks = chunk_text(text)
    for i, chunk in enumerate(chunks):
        vec = emb.embed_text(chunk)
        obj = {"text": chunk, "metadata": {"title": title, **metadata, "chunk_index": i}}
        id = str(uuid.uuid4())
        client.data_object.create(obj, cls, uuid=id, vector=vec)
    return {"status": "ok", "chunks": len(chunks)}
