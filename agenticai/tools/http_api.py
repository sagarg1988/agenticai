import requests

class HTTPAPITool:
    def run(self, args, session_id=None):
        url = args.get("url")
        method = args.get("method", "GET").upper()
        if not url:
            raise ValueError("url required")
        resp = requests.request(method, url, timeout=10)
        return {"status_code": resp.status_code, "text": resp.text}
