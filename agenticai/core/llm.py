"""
LLM Provider abstraction — wraps multiple LLM backends behind a single interface.

TODO:
- Support Anthropic Claude, Google Gemini, Azure OpenAI, and local Ollama.
- Retrieve API keys from a secrets manager (never hard-code).
- Add retry logic with exponential back-off for transient API errors.
- Implement cost tracking / token-usage logging.
"""
from __future__ import annotations

import logging
from typing import Any

from django.conf import settings

logger = logging.getLogger(__name__)


class LLMProvider:
    """
    Unified interface for calling LLM APIs.

    Supported backends (configured via LLM_BACKEND setting):
    - "openai" (default)

    TODO: add "anthropic", "google", "azure_openai", "ollama" backends.
    """

    def __init__(self, backend: str | None = None) -> None:
        self.backend = backend or getattr(settings, "LLM_BACKEND", "openai")
        self.model = getattr(settings, "LLM_MODEL", "gpt-4o")
        self._client = None  # lazy-initialised

    def _get_client(self) -> Any:
        if self._client is None:
            if self.backend == "openai":
                import openai  # noqa: PLC0415

                # TODO: fetch API key from secrets manager
                self._client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
            else:
                raise ValueError(f"Unknown LLM backend: {self.backend!r}")
        return self._client

    def complete(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.0,
        max_tokens: int = 2048,
    ) -> str:
        """
        Send *messages* to the LLM and return the assistant reply as a string.

        Args:
            messages: OpenAI-format list of {"role": ..., "content": ...} dicts.
            temperature: Sampling temperature (0 = deterministic).
            max_tokens: Maximum tokens in the completion.

        Returns:
            The assistant's reply string.
        """
        client = self._get_client()
        logger.info(
            "LLM complete backend=%s model=%s messages=%d",
            self.backend,
            self.model,
            len(messages),
        )
        if self.backend == "openai":
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content or ""
        raise NotImplementedError(f"complete() not implemented for backend '{self.backend}'")


def get_llm(backend: str | None = None) -> LLMProvider:
    """Factory function — return a configured LLMProvider instance."""
    return LLMProvider(backend=backend)
