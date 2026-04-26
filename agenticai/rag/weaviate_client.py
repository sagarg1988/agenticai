from urllib.parse import urlparse

import weaviate
from django.conf import settings


def get_weaviate_client():
    """Return a connected weaviate v4 WeaviateClient (use as context manager)."""
    parsed = urlparse(settings.WEAVIATE_URL)
    host = parsed.hostname or "weaviate"
    http_port = parsed.port or 8080
    secure = parsed.scheme == "https"
    grpc_port = int(getattr(settings, "WEAVIATE_GRPC_PORT", 50051))
    return weaviate.connect_to_custom(
        http_host=host,
        http_port=http_port,
        http_secure=secure,
        grpc_host=host,
        grpc_port=grpc_port,
        grpc_secure=False,
        skip_init_checks=True,
    )
