"""
HTTP API tool — makes configurable HTTP requests to external REST APIs.

TODO: add OAuth / API-key injection from a secure secrets store.
TODO: enforce an allow-list of permitted domains to prevent SSRF.
"""

from __future__ import annotations

import logging
from typing import Any

from agenticai.tools.fn_registry import BaseTool

logger = logging.getLogger(__name__)

# TODO: maintain an allow-list of permitted hostnames to prevent SSRF
_ALLOWED_SCHEMES = {"https"}


class HTTPAPITool(BaseTool):
    name = "http_api"

    def run(self, inputs: dict[str, Any]) -> dict:
        import httpx  # noqa: PLC0415

        url: str = inputs.get("url", "")
        method: str = inputs.get("method", "GET").upper()
        headers: dict = inputs.get("headers", {})
        body: dict | None = inputs.get("body")
        timeout: int = int(inputs.get("timeout", 15))

        # TODO: validate URL scheme and host against an allow-list
        logger.info("HTTPAPITool.run", extra={"method": method, "url": url})

        with httpx.Client(timeout=timeout) as client:
            response = client.request(method, url, headers=headers, json=body)
            response.raise_for_status()
            try:
                return {"status_code": response.status_code, "body": response.json()}
            except Exception:  # noqa: BLE001
                return {"status_code": response.status_code, "body": response.text}
