"""
Synthesizer — turns tool observations into a final human-readable answer.

TODO:
- Replace stub with a real LLM summarisation call via core.llm.
- Stream partial tokens to the HTTP response for low-latency UX.
- Support multi-modal outputs (tables, images) in the future.
"""
from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class Synthesizer:
    """Produces a final answer from user input and tool observations."""

    def __init__(self, agent_config: dict[str, Any]) -> None:
        self.agent_config = agent_config
        # TODO: initialise LLM client via core.llm.get_llm()

    def synthesize(
        self, user_input: str, observations: list[dict[str, Any]]
    ) -> str:
        """
        Combine *observations* into a natural-language answer for *user_input*.

        Stub implementation — concatenates observation results.
        Replace with a real LLM summarisation call.
        """
        logger.debug("Synthesizing answer from %d observations", len(observations))
        # TODO: call LLM with user_input + observations and return the response
        parts = []
        for obs in observations:
            if "result" in obs:
                parts.append(str(obs["result"]))
            elif "error" in obs:
                parts.append(f"[error: {obs['error']}]")
        return "\n".join(parts) if parts else "No result."
