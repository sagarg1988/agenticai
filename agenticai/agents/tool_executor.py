"""
Tool Executor — dispatches individual tool-call steps to registered tools.

TODO:
- Add timeout per tool call.
- Sandbox Python-function tool execution (restricted globals / subprocess).
- Log tool invocations to observability stack.
"""
from __future__ import annotations

import logging
from typing import Any

from tools.registry import ToolRegistry

logger = logging.getLogger(__name__)


class ToolExecutor:
    """
    Executes a single planner step by looking up the tool in the registry
    and calling it with the provided arguments.
    """

    def __init__(self, enabled_tools: list[str]) -> None:
        self.registry = ToolRegistry()
        self.enabled_tools = set(enabled_tools)

    def execute(self, step: dict[str, Any]) -> Any:
        """
        Execute the tool specified in *step* and return its result.

        step format: {"tool": "<name>", "args": {...}}
        """
        tool_name: str = step.get("tool", "")
        args: dict[str, Any] = step.get("args", {})

        if self.enabled_tools and tool_name not in self.enabled_tools:
            raise PermissionError(
                f"Tool '{tool_name}' is not enabled for this agent."
            )

        tool_fn = self.registry.get(tool_name)
        if tool_fn is None:
            raise ValueError(f"Unknown tool: '{tool_name}'")

        logger.info("Executing tool '%s' with args %s", tool_name, args)
        return tool_fn(**args)
