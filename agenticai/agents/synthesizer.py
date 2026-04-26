"""
Synthesizer — generates the final answer by feeding the goal + tool results
back to the LLM.

TODO: stream the final answer token-by-token to support real-time UX.
TODO: add citation/source attribution from tool results.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from agenticai.core.llm import get_llm

logger = logging.getLogger(__name__)

SYNTHESIZER_SYSTEM_PROMPT = """You are a helpful AI assistant.
You will be given a user goal and a list of tool execution results.
Synthesize a clear, concise final answer that directly addresses the goal.
Cite tool outputs where relevant. If any tool failed, acknowledge the gap.
"""


class Synthesizer:
    """Combines tool results into a final natural-language answer."""

    def synthesise(self, goal: str, tool_results: list[dict[str, Any]]) -> str:
        llm = get_llm()
        results_text = json.dumps(tool_results, indent=2, default=str)
        messages = [
            {"role": "system", "content": SYNTHESIZER_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"Goal: {goal}\n\n"
                    f"Tool results:\n{results_text}\n\n"
                    "Please provide the final answer."
                ),
            },
        ]
        response = llm.invoke(messages)
        answer = response.content if hasattr(response, "content") else str(response)
        logger.info("Synthesizer.synthesise", extra={"goal": goal, "answer_len": len(answer)})
        return answer
