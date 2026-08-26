"""Compile and run the Aid Desk LangGraph."""

from __future__ import annotations

import time
import uuid
from functools import lru_cache
from typing import Any

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from app.agents import nodes
from app.agents.state import CaseState

_checkpointer = MemorySaver()


def build_graph():
    graph = StateGraph(CaseState)
    graph.add_node("intake", nodes.intake_node)
    graph.add_node("triage", nodes.triage_node)
    graph.add_node("knowledge", nodes.knowledge_node)
    graph.add_node("integrity", nodes.integrity_node)
    graph.add_node("hitl_gate", nodes.hitl_gate_node)
    graph.add_node("matcher", nodes.matcher_node)
    graph.add_node("dispatch", nodes.dispatch_node)

    graph.add_edge(START, "intake")
    graph.add_edge("intake", "triage")
    graph.add_edge("triage", "knowledge")
    graph.add_edge("knowledge", "integrity")
    graph.add_conditional_edges(
        "integrity",
        nodes.route_after_integrity,
        {"hitl_gate": "hitl_gate", "matcher": "matcher"},
    )
    graph.add_conditional_edges(
        "hitl_gate",
        nodes.route_after_hitl,
        {"matcher": "matcher", "__end__": END},
    )
    graph.add_edge("matcher", "dispatch")
    graph.add_edge("dispatch", END)
    return graph.compile(checkpointer=_checkpointer)


@lru_cache
def get_graph():
    return build_graph()


async def run_pipeline(message: str, case_id: str | None = None) -> dict[str, Any]:
    graph = get_graph()
    cid = case_id or str(uuid.uuid4())
    config = {"configurable": {"thread_id": cid}}
    initial: CaseState = {
        "case_id": cid,
        "raw_message": message,
        "agent_trace": [],
        "started_at_ms": int(time.time() * 1000),
    }
    result = await graph.ainvoke(initial, config=config)
    return dict(result)


async def resume_after_hitl(
    case_id: str,
    decision: str,
    note: str | None = None,
) -> dict[str, Any]:
    graph = get_graph()
    config = {"configurable": {"thread_id": case_id}}
    result = await graph.ainvoke(
        {"hitl_decision": decision, "hitl_note": note or ""},
        config=config,
    )
    return dict(result)
