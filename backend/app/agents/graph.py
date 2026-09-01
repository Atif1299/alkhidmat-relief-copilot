"""Compile and run the Aid Desk LangGraph."""

from __future__ import annotations

import time
import uuid
from pathlib import Path
from typing import Any

from langgraph.graph import END, START, StateGraph

from app.agents import nodes
from app.agents.state import CaseState
from app.config import settings

_checkpointer: Any = None
_graph = None
_pg_pool: Any = None


def _checkpoint_path() -> Path:
    raw = settings.checkpoint_path.strip()
    if raw:
        return Path(raw)
    return settings.db_path.parent / "checkpoints.db"


async def init_graph() -> None:
    """Open durable checkpointer.

    Postgres checkpointer on Linux/Docker/GCP. On Windows, uvicorn uses
    ProactorEventLoop which psycopg async rejects — use SQLite checkpoints
    while the app DB remains Postgres.
    """
    global _checkpointer, _graph, _pg_pool
    if _graph is not None:
        return

    import sys

    use_postgres_checkpoint = settings.is_postgres and sys.platform != "win32"

    if use_postgres_checkpoint:
        from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
        from psycopg.rows import dict_row
        from psycopg_pool import AsyncConnectionPool

        _pg_pool = AsyncConnectionPool(
            conninfo=settings.psycopg_url,
            kwargs={
                "autocommit": True,
                "prepare_threshold": 0,
                "row_factory": dict_row,
            },
            open=False,
            min_size=1,
            max_size=5,
        )
        await _pg_pool.open()
        _checkpointer = AsyncPostgresSaver(_pg_pool)
        await _checkpointer.setup()
    else:
        import aiosqlite
        from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

        path = _checkpoint_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        # Prefer ./data next to backend when DB is Postgres on Windows
        if settings.is_postgres and not settings.checkpoint_path.strip():
            path = Path("./data/checkpoints.db")
            path.parent.mkdir(parents=True, exist_ok=True)
        conn = await aiosqlite.connect(str(path))
        _checkpointer = AsyncSqliteSaver(conn)
        await _checkpointer.setup()

    _graph = build_graph()


async def close_graph() -> None:
    """Release Postgres pool on shutdown."""
    global _pg_pool, _checkpointer, _graph
    if _pg_pool is not None:
        await _pg_pool.close()
        _pg_pool = None
    _checkpointer = None
    _graph = None


def build_graph():
    if _checkpointer is None:
        raise RuntimeError("Checkpointer not initialized — call await init_graph() first")
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
    return graph.compile(checkpointer=_checkpointer, interrupt_before=["hitl_gate"])


def get_graph():
    if _graph is None:
        raise RuntimeError("Graph not initialized — call await init_graph() at startup")
    return _graph


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
    await graph.ainvoke(initial, config=config)
    snapshot = await graph.aget_state(config)
    values = dict(snapshot.values or {})
    # Paused before hitl_gate — upstream ran but gate node did not
    if snapshot.next and "hitl_gate" in snapshot.next:
        pause = await nodes.finalize_hitl_pause(values)
        values = {**values, **pause}
    return values


async def resume_after_hitl(
    case_id: str,
    decision: str,
    note: str | None = None,
) -> dict[str, Any]:
    graph = get_graph()
    config = {"configurable": {"thread_id": case_id}}
    await graph.ainvoke(
        {"hitl_decision": decision, "hitl_note": note or ""},
        config=config,
    )
    snapshot = await graph.aget_state(config)
    return dict(snapshot.values or {})
