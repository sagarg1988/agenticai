"""
Basic smoke tests for the AgenticAI scaffold.

These tests verify that the core modules are importable and that
the key classes can be instantiated without errors.

TODO:
- Add integration tests with a real Weaviate instance (use pytest fixtures).
- Add API endpoint tests using DRF's APITestCase or pytest-django's client.
- Mock LLM and tool calls for deterministic unit tests.
"""
import pytest


def test_short_term_memory_basic():
    """ShortTermMemory should accept messages and return them in order."""
    from memory.short_term import ShortTermMemory

    mem = ShortTermMemory(max_messages=5)
    assert len(mem) == 0

    mem.add("user", "Hello")
    mem.add("assistant", "Hi there!")
    assert len(mem) == 2

    messages = mem.get_messages()
    assert messages[0]["role"] == "user"
    assert messages[1]["role"] == "assistant"


def test_short_term_memory_overflow():
    """ShortTermMemory should evict oldest messages when full."""
    from memory.short_term import ShortTermMemory

    mem = ShortTermMemory(max_messages=3)
    for i in range(5):
        mem.add("user", f"message {i}")

    assert len(mem) == 3
    messages = mem.get_messages()
    assert messages[0]["content"] == "message 2"


def test_tool_registry_noop():
    """ToolRegistry should return None for an unknown tool name."""
    from tools.registry import ToolRegistry

    registry = ToolRegistry()
    assert registry.get("__nonexistent_tool__") is None


def test_tool_registry_list():
    """ToolRegistry should list all registered tools."""
    from tools.registry import ToolRegistry

    registry = ToolRegistry()
    tools = registry.list_tools()
    assert isinstance(tools, list)
    # Built-in tools should be registered
    assert "web_search" in tools
    assert "db_query" in tools
    assert "http_api" in tools
    assert "python_fn" in tools


def test_db_query_rejects_non_select():
    """db_query tool should raise ValueError for non-SELECT SQL."""
    import django
    import os
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "aiagent.settings.base")

    from tools.db_query import db_query

    with pytest.raises(ValueError, match="Only SELECT queries are permitted"):
        db_query("DROP TABLE api_agent")


def test_planner_returns_steps(monkeypatch):
    """Planner.plan() should return a non-empty list of steps."""
    from agents.planner import Planner

    planner = Planner(agent_config={"tools": ["noop"]})
    steps = planner.plan("What is the capital of France?")
    assert isinstance(steps, list)
    assert len(steps) > 0
    assert "tool" in steps[0]


def test_synthesizer_basic():
    """Synthesizer.synthesize() should return a non-empty string."""
    from agents.synthesizer import Synthesizer

    synthesizer = Synthesizer(agent_config={})
    result = synthesizer.synthesize(
        "What is 2+2?",
        [{"step": {"tool": "noop", "args": {}}, "result": "4"}],
    )
    assert result == "4"


def test_synthesizer_no_observations():
    """Synthesizer should handle empty observations gracefully."""
    from agents.synthesizer import Synthesizer

    synthesizer = Synthesizer(agent_config={})
    result = synthesizer.synthesize("hello", [])
    assert result == "No result."
