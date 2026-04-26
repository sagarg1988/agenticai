"""
Agent Runner — orchestrates the plan → execute → synthesize loop.

Uses LangGraph to manage the agent graph state machine.

TODO:
- Add timeout/max-step guardrails.
- Persist intermediate steps to AgentRun.metadata.
- Integrate LangSmith tracing in production.
"""
from __future__ import annotations

import logging
from typing import Any

from agents.planner import Planner
from agents.synthesizer import Synthesizer
from agents.tool_executor import ToolExecutor

logger = logging.getLogger(__name__)


class AgentRunner:
    """
    Runs an agent for a given input string.

    The loop:
    1. Planner produces an ordered list of steps (tool calls).
    2. ToolExecutor executes each step and collects results.
    3. Synthesizer turns results into a final answer.
    """

    def __init__(self, agent_config: dict[str, Any]) -> None:
        self.agent_config = agent_config
        self.planner = Planner(agent_config)
        self.tool_executor = ToolExecutor(agent_config.get("tools", []))
        self.synthesizer = Synthesizer(agent_config)

    def run(self, user_input: str) -> str:
        """Execute the agent and return the final answer."""
        logger.info("AgentRunner starting run", extra={"input_preview": user_input[:80]})

        # Step 1: Plan
        steps = self.planner.plan(user_input)
        logger.debug("Planner produced steps: %s", steps)

        # Step 2: Execute tools
        observations: list[dict[str, Any]] = []
        for step in steps:
            try:
                result = self.tool_executor.execute(step)
                observations.append({"step": step, "result": result})
            except Exception as exc:  # noqa: BLE001
                logger.warning("Tool execution failed for step %s: %s", step, exc)
                observations.append({"step": step, "error": str(exc)})

        # Step 3: Synthesize
        answer = self.synthesizer.synthesize(user_input, observations)
        logger.info("AgentRunner finished run")
        return answer
