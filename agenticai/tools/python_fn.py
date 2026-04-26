"""
Python function execution tool — runs arbitrary Python code snippets.

⚠️  SECURITY WARNING: Executing untrusted code is dangerous.
TODO: sandbox execution using one of:
  - Docker-in-Docker (separate ephemeral container)
  - gVisor (runsc) restricted container
  - Pyodide (WASM) for pure-Python sandboxing
  - RestrictedPython for limited AST-based sandboxing

For now this uses exec() with a restricted globals dict — NOT safe for
untrusted input. Replace before deploying to production.
"""

from __future__ import annotations

import logging
from typing import Any

from agenticai.tools.fn_registry import BaseTool

logger = logging.getLogger(__name__)

# Minimal safe builtins — extend carefully
_SAFE_BUILTINS = {
    "__builtins__": {
        "print": print,
        "range": range,
        "len": len,
        "str": str,
        "int": int,
        "float": float,
        "list": list,
        "dict": dict,
        "tuple": tuple,
        "bool": bool,
        "abs": abs,
        "round": round,
        "sum": sum,
        "min": min,
        "max": max,
        "enumerate": enumerate,
        "zip": zip,
    }
}


class PythonFnTool(BaseTool):
    name = "python_fn"

    def run(self, inputs: dict[str, Any]) -> Any:
        code: str = inputs.get("code", "")
        # TODO: replace exec-based approach with a proper sandbox before production
        logger.warning("PythonFnTool: executing code via exec() — use sandbox in production")
        local_vars: dict = {}
        exec(code, dict(_SAFE_BUILTINS), local_vars)  # noqa: S102
        return local_vars.get("result")
