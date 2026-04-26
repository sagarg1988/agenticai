"""
Web search tool — wraps a search API (DuckDuckGo by default).

TODO: support additional providers (Bing, Google, Serper) via provider config.
TODO: add result caching to reduce redundant API calls.
"""

from __future__ import annotations

import logging
from typing import Any

from agenticai.tools.fn_registry import BaseTool

logger = logging.getLogger(__name__)

DDGS_URL = "https://api.duckduckgo.com/"


class WebSearchTool(BaseTool):
    name = "web_search"

    def run(self, inputs: dict[str, Any]) -> list[dict]:
        import httpx  # noqa: PLC0415

        query: str = inputs.get("query", "")
        max_results: int = int(inputs.get("max_results", 5))

        logger.info("WebSearchTool.run", extra={"query": query})

        # TODO: replace with authenticated search API for production reliability
        try:
            response = httpx.get(
                DDGS_URL,
                params={"q": query, "format": "json", "no_html": 1, "skip_disambig": 1},
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()
            results = data.get("RelatedTopics", [])[:max_results]
            return [{"title": r.get("Text", ""), "url": r.get("FirstURL", "")} for r in results if isinstance(r, dict)]
        except Exception as exc:  # noqa: BLE001
            logger.exception("WebSearchTool failed")
            return [{"error": str(exc)}]
