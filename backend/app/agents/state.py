"""LangGraph CaseState for Aid Desk pipeline."""

from __future__ import annotations

from typing import Annotated, Any, Optional, TypedDict


def dedupe_trace(steps: list) -> list:
    """Drop repeated agent steps (e.g. after HITL resume re-ran upstream nodes)."""
    seen: set[tuple[str, str, str]] = set()
    out: list = []
    for step in steps or []:
        if not isinstance(step, dict):
            continue
        key = (
            str(step.get("agent", "")),
            str(step.get("action", "")),
            str(step.get("detail", "")),
        )
        if key in seen:
            continue
        seen.add(key)
        out.append(step)
    return out


def merge_trace(left: list, right: list) -> list:
    return dedupe_trace((left or []) + (right or []))


class CaseState(TypedDict, total=False):
    case_id: str
    raw_message: str
    language: str
    extracted: dict[str, Any]
    category: str
    priority: str
    integrity: dict[str, Any]
    sop_hits: list[dict[str, Any]]
    matched_resources: list[dict[str, Any]]
    volunteer: Optional[dict[str, Any]]
    ticket_id: Optional[str]
    status: str
    agent_trace: Annotated[list[dict[str, Any]], merge_trace]
    requires_hitl: bool
    hitl_decision: Optional[str]
    hitl_note: Optional[str]
    notification: Optional[str]
    error: Optional[str]
    started_at_ms: int
