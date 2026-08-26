"""LangGraph CaseState for Aid Desk pipeline."""

from __future__ import annotations

from typing import Annotated, Any, Optional, TypedDict


def merge_trace(left: list, right: list) -> list:
    return (left or []) + (right or [])


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
