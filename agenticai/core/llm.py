import os
import openai

class LLMProvider:
    def __init__(self, provider=None):
        self.provider = provider or os.getenv("LLM_PROVIDER", "openai")
        if self.provider == "openai":
            openai.api_key = os.getenv("OPENAI_API_KEY")

    def generate(self, prompt, **kwargs):
        resp = openai.ChatCompletion.create(model=os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini"),
                                            messages=[{"role":"system","content":"You are an assistant."},{"role":"user","content":prompt}],
                                            temperature=kwargs.get("temperature",0.2),
                                            max_tokens=kwargs.get("max_tokens",512))
        return resp["choices"][0]["message"]["content"]
