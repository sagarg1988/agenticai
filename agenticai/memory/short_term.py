"""
Short-term (in-memory) conversation memory.

Stores recent messages for the duration of a single agent run.
TODO: persist short-term memory to Redis for multi-turn conversation support.
"""

from __future__ import annotations

from collections import deque
from typing import Any


class ShortTermMemory:
    """Ring-buffer of recent agent messages / observations."""

    def __init__(self, max_size: int = 20) -> None:
        self._buffer: deque[dict[str, Any]] = deque(maxlen=max_size)

    def add(self, role: str, content: str) -> None:
        self._buffer.append({"role": role, "content": content})

    def get_messages(self) -> list[dict[str, Any]]:
        return list(self._buffer)

    def clear(self) -> None:
        self._buffer.clear()

    def __len__(self) -> int:
        return len(self._buffer)
