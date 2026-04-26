"""
LLM provider factory.

Returns a LangChain ChatOpenAI instance by default.

TODO: abstract behind a BaseLLMProvider interface to support:
  - Azure OpenAI
  - Anthropic Claude
  - Local models via Ollama / LlamaCpp
  - Google Gemini

TODO: store API keys in a secrets manager (AWS Secrets Manager, Vault) and
      retrieve them at runtime — never hardcode them or read from plain .env in prod.
"""

from __future__ import annotations

import os

_LLM_INSTANCE = None


def get_llm():
    """Return a shared LLM instance (lazy-initialised)."""
    global _LLM_INSTANCE  # noqa: PLW0603
    if _LLM_INSTANCE is None:
        from langchain_openai import ChatOpenAI  # noqa: PLC0415

        # TODO: validate OPENAI_API_KEY is present and raise descriptive error if not
        _LLM_INSTANCE = ChatOpenAI(
            api_key=os.environ.get("OPENAI_API_KEY", ""),  # TODO: use secrets manager
            model=os.environ.get("OPENAI_MODEL", "gpt-4o"),
            temperature=0,
        )
    return _LLM_INSTANCE
