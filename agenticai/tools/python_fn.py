"""
Python Function tool — executes arbitrary Python code snippets.

TODO (CRITICAL):
- Implement a proper sandbox (RestrictedPython, subprocess isolation,
  gVisor / Firecracker micro-VM, or a dedicated code-execution service).
- Currently runs code in the main interpreter with NO sandboxing.
  DO NOT expose this tool to untrusted inputs in production.
- Add resource limits (CPU time, memory) before enabling in production.
"""
from __future__ import annotations

import logging
import traceback
from io import StringIO
from contextlib import redirect_stdout

from tools.registry import register

logger = logging.getLogger(__name__)


@register("python_fn")
def python_fn(code: str, inputs: dict | None = None) -> str:
    """
    Execute *code* in a restricted local scope and return stdout output.

    Args:
        code: Python source code to execute.
        inputs: Optional dict of variables injected into the execution scope.

    Returns:
        Captured stdout as a string.

    WARNING: This is NOT sandboxed. See module TODO above.
    """
    logger.warning("python_fn executing code (NOT sandboxed): %r", code[:80])
    local_scope: dict = dict(inputs or {})
    stdout_capture = StringIO()
    try:
        with redirect_stdout(stdout_capture):
            exec(code, {"__builtins__": {}}, local_scope)  # noqa: S102 TODO: sandbox
    except Exception:  # noqa: BLE001
        return f"Error:\n{traceback.format_exc()}"
    return stdout_capture.getvalue()
