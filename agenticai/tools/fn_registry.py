"""
Function Registry tool — registers and invokes named Python callables.

Allows agents to call pre-registered Python functions by name,
providing a safer alternative to the python_fn tool for known operations.
"""
from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any

from tools.registry import register

logger = logging.getLogger(__name__)

_FUNCTION_REGISTRY: dict[str, Callable[..., Any]] = {}


def register_function(name: str, fn: Callable[..., Any]) -> None:
    """Register a callable under *name* for agent invocation."""
    _FUNCTION_REGISTRY[name] = fn
    logger.debug("Registered function: %s", name)


@register("fn_registry_call")
def fn_registry_call(name: str, kwargs: dict | None = None) -> Any:
    """
    Invoke a pre-registered function by *name* with optional *kwargs*.

    Args:
        name: Name of the registered function.
        kwargs: Keyword arguments to pass to the function.

    Returns:
        Return value of the function.
    """
    if name not in _FUNCTION_REGISTRY:
        raise ValueError(f"Function '{name}' is not registered.")
    logger.info("fn_registry_call name=%r kwargs=%r", name, kwargs)
    return _FUNCTION_REGISTRY[name](**(kwargs or {}))
