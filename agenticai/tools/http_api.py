"""
HTTP API tool — calls external HTTP endpoints on behalf of the agent.

TODO:
- Add OAuth / API-key header injection from a secrets store.
- Enforce an allowlist of permitted domains in production.
- Add retry logic with exponential back-off.
"""
from __future__ import annotations

import logging
from typing import Any

import httpx

from tools.registry import register

logger = logging.getLogger(__name__)

# TODO: load allowed domains from settings / environment variable
_ALLOWED_DOMAINS: set[str] = set()  # empty = allow all (restrict in production)


@register("http_api")
def http_api(
    url: str,
    method: str = "GET",
    headers: dict | None = None,
    json: Any = None,
    params: dict | None = None,
    timeout: float = 15.0,
) -> dict:
    """
    Make an HTTP request and return the JSON response.

    Args:
        url: Target URL.
        method: HTTP method (GET, POST, PUT, DELETE, …).
        headers: Optional request headers.
        json: Optional JSON body (for POST/PUT).
        params: Optional query parameters.
        timeout: Request timeout in seconds.

    Returns:
        Dict with keys: status_code, headers, body.
    """
    logger.info("http_api %s %s", method.upper(), url)
    # TODO: enforce _ALLOWED_DOMAINS allowlist
    with httpx.Client(timeout=timeout) as client:
        response = client.request(
            method=method.upper(),
            url=url,
            headers=headers or {},
            json=json,
            params=params or {},
        )
    return {
        "status_code": response.status_code,
        "headers": dict(response.headers),
        "body": response.json() if "application/json" in response.headers.get("content-type", "") else response.text,
    }
