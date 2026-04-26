import weaviate.classes as wvc
from django.conf import settings

from rag.weaviate_client import get_weaviate_client


class MemoryRetriever:
    def __init__(self):
        self.class_name = "Memory"

    def retrieve(self, session_id, query, top_k=8):
        from rag.embeddings import EmbeddingProvider
        emb = EmbeddingProvider().embed_text(query)
        try:
            with get_weaviate_client() as client:
                collection = client.collections.get(self.class_name)
                response = collection.query.near_vector(
                    near_vector=emb,
                    limit=top_k,
                    return_metadata=wvc.query.MetadataQuery(distance=True),
                )
                items = []
                for obj in response.objects:
                    items.append({
                        "text": obj.properties.get("text"),
                        "metadata": obj.properties.get("metadata"),
                        "id": str(obj.uuid),
                        "distance": obj.metadata.distance if obj.metadata else None,
                    })
                return items
        except Exception:
            return []
