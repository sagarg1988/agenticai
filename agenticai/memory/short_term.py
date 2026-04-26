import redis
import os

class ShortTermMemory:
    def __init__(self):
        url = os.getenv("REDIS_URL", "redis://redis:6379/0")
        self.client = redis.from_url(url)

    def append_message(self, session_id, role, content):
        key = f"session:{session_id}:messages"
        self.client.rpush(key, f"{role}:{content}")

    def get_recent(self, session_id, count=20):
        key = f"session:{session_id}:messages"
        return self.client.lrange(key, -count, -1)
