"""
Basic smoke tests for the AgenticAI scaffold.

Run with: pytest agenticai/tests/
"""

import pytest


# ---------------------------------------------------------------------------
# ShortTermMemory
# ---------------------------------------------------------------------------
class TestShortTermMemory:
    def test_add_and_retrieve(self):
        from agenticai.memory.short_term import ShortTermMemory

        mem = ShortTermMemory(max_size=3)
        mem.add("user", "Hello")
        mem.add("assistant", "Hi there")
        messages = mem.get_messages()
        assert len(messages) == 2
        assert messages[0]["role"] == "user"
        assert messages[1]["content"] == "Hi there"

    def test_max_size_eviction(self):
        from agenticai.memory.short_term import ShortTermMemory

        mem = ShortTermMemory(max_size=2)
        mem.add("user", "msg1")
        mem.add("user", "msg2")
        mem.add("user", "msg3")
        assert len(mem) == 2
        assert mem.get_messages()[0]["content"] == "msg2"

    def test_clear(self):
        from agenticai.memory.short_term import ShortTermMemory

        mem = ShortTermMemory()
        mem.add("user", "Hello")
        mem.clear()
        assert len(mem) == 0


# ---------------------------------------------------------------------------
# ToolRegistry
# ---------------------------------------------------------------------------
class TestToolRegistry:
    def test_default_tools_registered(self):
        from agenticai.tools.registry import ToolRegistry

        registry = ToolRegistry()
        tools = registry.list_tools()
        assert "web_search" in tools
        assert "db_query" in tools
        assert "python_fn" in tools
        assert "http_api" in tools

    def test_get_unknown_tool_returns_none(self):
        from agenticai.tools.registry import ToolRegistry

        registry = ToolRegistry()
        assert registry.get("nonexistent_tool") is None


# ---------------------------------------------------------------------------
# RAG text chunking
# ---------------------------------------------------------------------------
class TestTextChunking:
    def test_chunk_short_text(self):
        from agenticai.rag.ingest import _chunk_text

        chunks = _chunk_text("Hello world", size=100, overlap=10)
        assert chunks == ["Hello world"]

    def test_chunk_produces_overlap(self):
        from agenticai.rag.ingest import _chunk_text

        text = "a" * 20
        chunks = _chunk_text(text, size=10, overlap=5)
        # With size=10, overlap=5: start positions 0, 5, 10, 15 → 4 chunks
        assert len(chunks) == 4
        # Each chunk (except possibly last) should be size chars
        assert chunks[0] == "a" * 10


# ---------------------------------------------------------------------------
# API models (no DB required — just import checks)
# ---------------------------------------------------------------------------
class TestModelsImport:
    def test_models_importable(self):
        pytest.importorskip("django", reason="Django not installed")
        import importlib

        mod = importlib.import_module("agenticai.api.models")
        assert hasattr(mod, "Agent")
        assert hasattr(mod, "AgentRun")


# ---------------------------------------------------------------------------
# Planner JSON parsing fallback
# ---------------------------------------------------------------------------
class TestPlannerFallback:
    def test_invalid_json_returns_empty_plan(self, monkeypatch):
        from agenticai.agents import planner as planner_mod

        class _FakeLLM:
            def invoke(self, messages):
                class R:
                    content = "this is not json"

                return R()

        monkeypatch.setattr(planner_mod, "get_llm", lambda: _FakeLLM())
        from agenticai.agents.planner import Planner

        p = Planner()
        result = p.plan("do something")
        assert result == []
