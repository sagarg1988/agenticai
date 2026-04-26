"""
Planner — decomposes a high-level goal into an ordered list of tool-call steps
by prompting the LLM.

TODO: add few-shot examples and structured output validation (Pydantic).
TODO: support multi-step re-planning when a tool fails.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from agenticai.core.llm import get_llm

logger = logging.getLogger(__name__)

PLANNER_SYSTEM_PROMPT = """You are an expert AI agent planner.
Given a user goal, decompose it into a minimal, ordered list of tool-call steps.
Return ONLY valid JSON — a list of objects, each with keys:
  "tool"   : string — the tool name
  "input"  : object — parameters to pass to the tool
  "reason" : string — why this step is needed

Available tools: web_search, db_query, python_fn, http_api
"""


class Planner:
    """Converts a natural-language goal into a structured execution plan."""

    def plan(self, goal: str) -> list[dict[str, Any]]:
        llm = get_llm()
        messages = [
            {"role": "system", "content": PLANNER_SYSTEM_PROMPT},
            {"role": "user", "content": f"Goal: {goal}"},
        ]
        response = llm.invoke(messages)
        raw = response.content if hasattr(response, "content") else str(response)

        try:
            plan = json.loads(raw)
        except json.JSONDecodeError:
            logger.warning("Planner: could not parse LLM response as JSON; returning empty plan", extra={"raw": raw})
            plan = []

        logger.info("Planner.plan", extra={"goal": goal, "steps": len(plan)})
        return plan
