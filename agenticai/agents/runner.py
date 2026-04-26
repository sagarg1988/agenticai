"""
Agent runner — orchestrates the full plan → execute → synthesise loop
using LangGraph as the state machine.

TODO: add streaming support via LangGraph streaming API.
TODO: add human-in-the-loop pause/resume nodes.
"""

from __future__ import annotations

import logging
from typing import Any

from langgraph.graph import END, StateGraph

from agenticai.agents.planner import Planner
from agenticai.agents.synthesizer import Synthesizer
from agenticai.agents.tool_executor import ToolExecutor

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# State schema
# ---------------------------------------------------------------------------
class AgentState(dict):
    """Typed dict-like state object passed between graph nodes."""

    goal: str
    plan: list[dict]
    tool_results: list[dict]
    final_answer: str
    error: str


# ---------------------------------------------------------------------------
# Graph nodes
# ---------------------------------------------------------------------------
def plan_node(state: AgentState) -> AgentState:
    planner = Planner()
    state["plan"] = planner.plan(state["goal"])
    return state


def execute_node(state: AgentState) -> AgentState:
    executor = ToolExecutor()
    results = []
    for step in state.get("plan", []):
        result = executor.execute(step)
        results.append(result)
    state["tool_results"] = results
    return state


def synthesise_node(state: AgentState) -> AgentState:
    synth = Synthesizer()
    state["final_answer"] = synth.synthesise(
        goal=state["goal"],
        tool_results=state["tool_results"],
    )
    return state


# ---------------------------------------------------------------------------
# Graph definition
# ---------------------------------------------------------------------------
def _build_graph() -> StateGraph:
    graph = StateGraph(AgentState)
    graph.add_node("plan", plan_node)
    graph.add_node("execute", execute_node)
    graph.add_node("synthesise", synthesise_node)
    graph.set_entry_point("plan")
    graph.add_edge("plan", "execute")
    graph.add_edge("execute", "synthesise")
    graph.add_edge("synthesise", END)
    return graph.compile()


_graph = _build_graph()


class AgentRunner:
    """High-level interface to run the agent graph."""

    def run(self, goal: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        initial_state: AgentState = AgentState(
            goal=goal,
            plan=[],
            tool_results=[],
            final_answer="",
            error="",
        )
        if context:
            initial_state.update(context)

        logger.info("AgentRunner.run", extra={"goal": goal})
        result = _graph.invoke(initial_state)
        return dict(result)
