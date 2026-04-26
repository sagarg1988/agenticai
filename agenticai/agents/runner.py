from typing import Any, Dict
from memory.retriever import MemoryRetriever
from agents.planner import Planner
from agents.tool_executor import ToolExecutor
from agents.synthesizer import Synthesizer
from memory.short_term import ShortTermMemory

class AgentRunner:
    def __init__(self, embedding_provider=None, llm_provider=None):
        self.memory_retriever = MemoryRetriever()
        self.short_term = ShortTermMemory()
        self.planner = Planner(llm_provider=llm_provider)
        self.tool_executor = ToolExecutor()
        self.synthesizer = Synthesizer(llm_provider=llm_provider)

    def run(self, session_id: str, input: str, options: Dict[str, Any], user=None) -> Dict[str, Any]:
        if len(input) > 20000:
            raise ValueError("Input too long")

        retrieved = self.memory_retriever.retrieve(session_id=session_id, query=input, top_k=8)
        plan = self.planner.create_plan(input_text=input, memories=retrieved)
        exec_results = self.tool_executor.execute_plan(plan, session_id=session_id)
        response = self.synthesizer.synthesize(input_text=input, plan=plan, exec_results=exec_results, memories=retrieved)
        self.short_term.append_message(session_id, "assistant", response.get("response", ""))
        return response
