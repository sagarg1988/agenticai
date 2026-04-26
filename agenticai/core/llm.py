import os
import json
import httpx
from openai import OpenAI


class LLMProvider:
    def __init__(self, provider=None):
        self.provider = (provider or os.getenv("LLM_PROVIDER", "openai")).lower()
        self.openai_model = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434").rstrip("/")
        self.ollama_model = os.getenv("OLLAMA_MODEL", "llama3")
        self.request_timeout = float(os.getenv("LLM_REQUEST_TIMEOUT", "60"))

        if self.provider == "openai":
            self._openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def generate(self, prompt, **kwargs):
        if self.provider == "ollama":
            return self._generate_ollama(prompt, **kwargs)
        if self.provider == "openai":
            return self._generate_openai(prompt, **kwargs)
        raise ValueError(f"Unsupported LLM provider: {self.provider}")

    def _generate_openai(self, prompt, **kwargs):
        resp = self._openai_client.chat.completions.create(
            model=kwargs.get("model", self.openai_model),
            messages=[
                {"role": "system", "content": "You are an assistant."},
                {"role": "user", "content": prompt},
            ],
            temperature=kwargs.get("temperature", 0.2),
            max_tokens=kwargs.get("max_tokens", 512),
        )
        return resp.choices[0].message.content

    def _generate_ollama(self, prompt, **kwargs):
        payload = {
            "model": kwargs.get("model", self.ollama_model),
            "messages": [
                {"role": "system", "content": "You are an assistant."},
                {"role": "user", "content": prompt},
            ],
            "stream": False,
            "options": {
                "temperature": kwargs.get("temperature", 0.2),
            },
        }

        with httpx.Client(timeout=self.request_timeout) as client:
            response = client.post(f"{self.ollama_base_url}/api/chat", json=payload)
            response.raise_for_status()
            data = response.json()

        message = data.get("message", {})
        content = message.get("content")
        if not content:
            raise ValueError(f"Invalid Ollama response payload: {json.dumps(data)[:500]}")
        return content
