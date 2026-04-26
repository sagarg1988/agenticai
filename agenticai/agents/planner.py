from tenacity import retry, stop_after_attempt, wait_exponential
from core.llm import LLMProvider

class Planner:
    def __init__(self, llm_provider: LLMProvider=None):
        self.llm = llm_provider or LLMProvider()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    def create_plan(self, input_text: str, memories=None):
        prompt = self._build_prompt(input_text, memories)
        raw = self.llm.generate(prompt)
        try:
            import json
            plan = json.loads(raw)
        except Exception:
            plan = {"plan_id": "fallback", "steps": [{"id":"s1","type":"synthesize","tool":"llm_synth","args":{}}]}
        return plan

    def _build_prompt(self, input_text, memories):
        return f"You are a planner. User: {input_text}\\nMemories: {memories}\\nReturn a JSON plan."
