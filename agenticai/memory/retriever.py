from urllib.parse import urlparse

import weaviate
import weaviate.classes as wvc
from django.conf import settings


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


class MemoryRetriever:
    def __init__(self):
        self.class_name = "Memory"

    def retrieve(self, session_id, query, top_k=8):
        from rag.embeddings import EmbeddingProvider
        emb = EmbeddingProvider().embed_text(query)
        try:
            with _connect() as client:
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
