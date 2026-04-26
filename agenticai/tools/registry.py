"""
Tool registry — central catalogue of all available tools.

Tools are registered by name and retrieved by the ToolExecutor at runtime.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agenticai.tools.fn_registry import BaseTool

logger = logging.getLogger(__name__)


class ToolRegistry:
    """Singleton-style registry that maps tool names to BaseTool instances."""

    _tools: dict[str, "BaseTool"] = {}
    _initialised: bool = False

    def __init__(self) -> None:
        if not ToolRegistry._initialised:
            self._register_defaults()
            ToolRegistry._initialised = True

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------
    @classmethod
    def register(cls, tool: "BaseTool") -> None:
        logger.debug("ToolRegistry.register", extra={"name": tool.name})
        cls._tools[tool.name] = tool

    # ------------------------------------------------------------------
    # Lookup
    # ------------------------------------------------------------------
    def get(self, name: str) -> "BaseTool | None":
        return ToolRegistry._tools.get(name)

    def list_tools(self) -> list[str]:
        return list(ToolRegistry._tools.keys())

    # ------------------------------------------------------------------
    # Default tools
    # ------------------------------------------------------------------
    def _register_defaults(self) -> None:
        from agenticai.tools.db_query import DBQueryTool
        from agenticai.tools.http_api import HTTPAPITool
        from agenticai.tools.python_fn import PythonFnTool
        from agenticai.tools.web_search import WebSearchTool

        for tool in [WebSearchTool(), DBQueryTool(), PythonFnTool(), HTTPAPITool()]:
            ToolRegistry.register(tool)
