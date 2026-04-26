"""
Planner — converts user input into an ordered sequence of tool-call steps.

TODO:
- Replace the stub implementation with a real LLM call using core.llm.
- Consider ReAct / function-calling prompts for reliable step extraction.
- Add retry logic for malformed LLM output.
"""
from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class Planner:
    """
    Produces a plan (list of steps) from user input.

    Each step is a dict with at minimum:
        {"tool": "<tool_name>", "args": {...}}
    """

    def __init__(self, agent_config: dict[str, Any]) -> None:
        self.agent_config = agent_config
        # TODO: initialise LLM client via core.llm.get_llm()

    def plan(self, user_input: str) -> list[dict[str, Any]]:
        """
        Convert *user_input* into an ordered list of tool-call steps.

        Stub implementation — returns a single no-op step.
        Replace with a real LLM planning prompt.
        """
        logger.debug("Planning for input: %s", user_input[:80])
        # TODO: call LLM with system_prompt + user_input + available tools schema
        return [
            {
                "tool": "noop",
                "args": {"query": user_input},
            }
        ]
