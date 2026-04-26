"""
Web Search tool — performs a web search and returns top results.

TODO:
- Choose a production search provider (SerpAPI, Brave Search, Bing, etc.)
  and store the API key in secrets manager.
- Add rate limiting and response caching.
"""
from __future__ import annotations

import logging

import httpx

from tools.registry import register

logger = logging.getLogger(__name__)

SEARCH_ENDPOINT = "https://api.search.example.com/search"  # TODO: replace with real endpoint


@register("web_search")
def web_search(query: str, num_results: int = 5) -> list[dict]:
    """
    Search the web for *query* and return up to *num_results* results.

    Returns a list of dicts: [{"title": ..., "url": ..., "snippet": ...}]
    """
    logger.info("web_search query=%r", query)
    # TODO: replace stub with a real search API call
    # Example using SerpAPI:
    # response = httpx.get(
    #     "https://serpapi.com/search",
    #     params={"q": query, "num": num_results, "api_key": settings.SERPAPI_KEY},
    #     timeout=10,
    # )
    # response.raise_for_status()
    # return response.json().get("organic_results", [])
    return [
        {
            "title": f"Result for '{query}'",
            "url": "https://example.com",
            "snippet": "Stub result — replace with real search API.",
        }
    ]
