"""
Short-term memory — in-process sliding-window conversation buffer.

Holds the most recent N messages for a single agent run session.
This is transient and not persisted between runs.

TODO:
- Consider using Redis for shared short-term memory across workers.
- Add token-count-based truncation instead of (or in addition to) message-count.
"""
from __future__ import annotations

from collections import deque
from typing import Any


class ShortTermMemory:
    """
    A sliding-window buffer of the most recent conversation messages.

    Args:
        max_messages: Maximum number of messages to retain.
    """

    def __init__(self, max_messages: int = 20) -> None:
        self._buffer: deque[dict[str, Any]] = deque(maxlen=max_messages)

    def add(self, role: str, content: str, metadata: dict | None = None) -> None:
        """Append a new message to the buffer."""
        self._buffer.append(
            {"role": role, "content": content, "metadata": metadata or {}}
        )

    def get_messages(self) -> list[dict[str, Any]]:
        """Return the current buffer as an ordered list (oldest first)."""
        return list(self._buffer)

    def clear(self) -> None:
        """Clear all messages from the buffer."""
        self._buffer.clear()

    def __len__(self) -> int:
        return len(self._buffer)
