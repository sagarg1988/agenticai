import os
import openai

class EmbeddingProvider:
    def __init__(self, provider=None):
        self.provider = provider or os.getenv("EMBEDDING_PROVIDER", "openai")
        if self.provider == "openai":
            openai.api_key = os.getenv("OPENAI_API_KEY")

    def embed_text(self, text):
        resp = openai.Embedding.create(model="text-embedding-3-small", input=text)
        return resp["data"][0]["embedding"]
