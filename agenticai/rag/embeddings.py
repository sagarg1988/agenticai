import os
from openai import OpenAI


class EmbeddingProvider:
    def __init__(self, provider=None):
        self.provider = provider or os.getenv("EMBEDDING_PROVIDER", "openai")
        if self.provider == "openai":
            self._client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def embed_text(self, text):
        resp = self._client.embeddings.create(model="text-embedding-3-small", input=text)
        return resp.data[0].embedding
