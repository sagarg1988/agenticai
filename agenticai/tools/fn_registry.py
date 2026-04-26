"""
Base tool interface — all tools must subclass BaseTool and implement .run().
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseTool(ABC):
    """Abstract base class for all AgenticAI tools."""

    name: str  # unique tool identifier used in the plan

    @abstractmethod
    def run(self, inputs: dict[str, Any]) -> Any:
        """Execute the tool with the given inputs and return the result."""
        ...
