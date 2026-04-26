"""
Tool executor — dispatches a single plan step to the appropriate tool.

TODO: add retry logic with exponential back-off.
TODO: enforce per-tool execution timeouts.
"""

from __future__ import annotations

import logging
from typing import Any

from agenticai.tools.registry import ToolRegistry

logger = logging.getLogger(__name__)


class ToolExecutor:
    """Executes a single plan step by looking up and calling the registered tool."""

    def __init__(self) -> None:
        self._registry = ToolRegistry()

    def execute(self, step: dict[str, Any]) -> dict[str, Any]:
        tool_name: str = step.get("tool", "")
        tool_input: dict = step.get("input", {})

        logger.info("ToolExecutor.execute", extra={"tool": tool_name, "input": tool_input})

        tool = self._registry.get(tool_name)
        if tool is None:
            error_msg = f"Tool '{tool_name}' not found in registry"
            logger.error(error_msg)
            return {"tool": tool_name, "error": error_msg, "output": None}

        try:
            output = tool.run(tool_input)
            return {"tool": tool_name, "output": output, "error": None}
        except Exception as exc:  # noqa: BLE001
            logger.exception("Tool execution failed", extra={"tool": tool_name})
            return {"tool": tool_name, "output": None, "error": str(exc)}
