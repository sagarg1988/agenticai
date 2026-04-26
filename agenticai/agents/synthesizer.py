from core.llm import LLMProvider
import json

class Synthesizer:
    def __init__(self, llm_provider=None):
        self.llm = llm_provider or LLMProvider()

    def synthesize(self, input_text, plan, exec_results, memories):
        context = "\\n\\n".join([m.get("text","") for m in (memories or [])[:5]])
        tool_summaries = "\\n".join([f"{k}: {v}" for k,v in exec_results.items()])
        prompt = f"""
User: {input_text}
Context: {context}
Tool outputs: {tool_summaries}
Plan: {plan}
Return JSON: {{ \"response\":\"...\", \"sources\":[], \"plan_summary\":\"...\" }}
"""
        raw = self.llm.generate(prompt)
        try:
            return json.loads(raw)
        except Exception:
            return {"response": raw, "sources": [], "plan_summary": ""}
