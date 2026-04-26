"""
Tool Registry — central lookup for all registered tools.

Tools are registered by name and can be looked up by the ToolExecutor.
"""
from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any

logger = logging.getLogger(__name__)

# Global registry: maps tool name -> callable
_REGISTRY: dict[str, Callable[..., Any]] = {}


def register(name: str) -> Callable:
    """Decorator to register a function as a named tool."""

    def decorator(fn: Callable) -> Callable:
        _REGISTRY[name] = fn
        logger.debug("Registered tool: %s", name)
        return fn

    return decorator


class ToolRegistry:
    """Interface for looking up registered tools."""

    def get(self, name: str) -> Callable[..., Any] | None:
        return _REGISTRY.get(name)

    def list_tools(self) -> list[str]:
        return list(_REGISTRY.keys())


# Import built-in tools so they auto-register on import
def _load_builtin_tools() -> None:
    from tools import db_query, fn_registry, http_api, python_fn, web_search  # noqa: F401


_load_builtin_tools()
