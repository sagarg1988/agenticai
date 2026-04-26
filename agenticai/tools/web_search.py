import os, requests
from tenacity import retry, stop_after_attempt, wait_exponential

class WebSearchTool:
    def __init__(self, provider="serpapi"):
        self.provider = provider
        self.api_key = os.getenv("SERPAPI_KEY")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, max=8))
    def run(self, args, session_id=None):
        q = args.get("q")
        if not q:
            raise ValueError("q required")
        # TODO: implement real provider calls
        return {"results": []}
