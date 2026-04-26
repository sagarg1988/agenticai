import pytest
from core.llm import LLMProvider


def test_unsupported_provider_raises():
    provider = LLMProvider(provider="not-a-provider")
    with pytest.raises(ValueError):
        provider.generate("hello")


def test_ollama_generate_parses_response(monkeypatch):
    provider = LLMProvider(provider="ollama")

    class DummyResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"message": {"content": "local-ok"}}

    class DummyClient:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def post(self, url, json):
            assert url.endswith("/api/chat")
            assert json["stream"] is False
            return DummyResponse()

    monkeypatch.setattr("core.llm.httpx.Client", DummyClient)

    assert provider.generate("hi") == "local-ok"


def test_ollama_invalid_payload_raises(monkeypatch):
    provider = LLMProvider(provider="ollama")

    class DummyResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"message": {}}

    class DummyClient:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def post(self, url, json):
            return DummyResponse()

    monkeypatch.setattr("core.llm.httpx.Client", DummyClient)

    with pytest.raises(ValueError):
        provider.generate("hi")

