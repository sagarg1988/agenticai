import weaviate
from django.conf import settings

class MemoryRetriever:
    def __init__(self):
        self.client = weaviate.Client(url=settings.WEAVIATE_URL)
        self.class_name = "Memory"

    def retrieve(self, session_id, query, top_k=8):
        from rag.embeddings import EmbeddingProvider
        emb = EmbeddingProvider().embed_text(query)
        try:
            res = self.client.query.get(self.class_name, ["text", "metadata", "_additional { id certainty }"]).with_near_vector({"vector": emb}).with_limit(top_k).do()
            items = []
            for r in (res.get("data", {}).get("Get", {}).get(self.class_name, []) or []):
                items.append({
                    "text": r.get("text"),
                    "metadata": r.get("metadata"),
                    "id": r.get("_additional", {}).get("id"),
                    "certainty": r.get("_additional", {}).get("certainty")
                })
            return items
        except Exception:
            return []
