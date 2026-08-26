"""Build product timeline stages from case + events + agent_trace."""

from __future__ import annotations

from typing import Any, Optional

from app.db.models import Case


STAGE_ORDER = [
    "requested",
    "triaged",
    "knowledge",
    "integrity_checked",
    "pending_hitl",
    "matched",
    "dispatched",
    "rejected",
    "closed",
]


def _find_event(events: list[dict], *types: str) -> Optional[dict]:
    for event in events:
        if event.get("event_type") in types:
            return event
    return None


def _find_trace(trace: list[dict], agent: str) -> Optional[dict]:
    for step in trace or []:
        if step.get("agent") == agent:
            return step
    return None


def build_timeline(case: Case, events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return ordered stages with status: done | active | pending | skipped."""
    trace = case.agent_trace or []
    stages: list[dict[str, Any]] = []

    def add(
        key: str,
        label: str,
        *,
        done: bool,
        active: bool = False,
        skipped: bool = False,
        at: Optional[str] = None,
        detail: Optional[str] = None,
    ) -> None:
        state = "skipped" if skipped else ("active" if active else ("done" if done else "pending"))
        stages.append(
            {
                "key": key,
                "label": label,
                "state": state,
                "at": at,
                "detail": detail,
            }
        )

    created = case.created_at.isoformat() if case.created_at else None
    add("requested", "Requested", done=True, at=created, detail=case.raw_message[:120] if case.raw_message else None)

    triaged_ev = _find_event(events, "triaged") or _find_trace(trace, "Triage")
    add(
        "triaged",
        "Triaged",
        done=bool(case.category) or bool(triaged_ev),
        at=(triaged_ev or {}).get("created_at") or (triaged_ev or {}).get("ts_ms"),
        detail=f"{case.category or ''} / {case.priority or ''}".strip(" /"),
    )

    know_ev = _find_event(events, "sop_retrieved") or _find_trace(trace, "Knowledge")
    sop_titles = ", ".join(h.get("title", "") for h in (case.sop_hits or []) if h.get("title"))
    add(
        "knowledge",
        "Knowledge / SOPs",
        done=bool(know_ev) or bool(case.sop_hits),
        at=(know_ev or {}).get("created_at") or (know_ev or {}).get("ts_ms"),
        detail=sop_titles or (know_ev or {}).get("detail"),
    )

    integ_ev = _find_event(events, "integrity_checked", "risk_cleared", "escalated")
    integ_tr = _find_trace(trace, "Integrity")
    add(
        "integrity_checked",
        "Integrity checked",
        done=bool(integ_ev or integ_tr or case.risk_score is not None),
        at=(integ_ev or {}).get("created_at"),
        detail=(integ_ev or {}).get("detail") or (integ_tr or {}).get("detail"),
    )

    hitl_needed = bool(case.requires_hitl or case.hitl_decision or case.status == "pending_hitl")
    if hitl_needed or case.status == "pending_hitl":
        add(
            "pending_hitl",
            "Awaiting supervisor",
            done=case.hitl_decision in ("approve", "reject") or case.status in ("dispatched", "rejected", "closed"),
            active=case.status == "pending_hitl",
            at=None,
            detail=case.hitl_decision or "pending",
        )
    else:
        add("pending_hitl", "Awaiting supervisor", done=False, skipped=True, detail="Not required")

    matched_ev = _find_event(events, "resources_matched", "matched")
    matched_tr = _find_trace(trace, "Matcher")
    add(
        "matched",
        "Matched",
        done=bool(matched_ev or matched_tr or case.matched_resource_id)
        or case.status in ("dispatched", "closed"),
        at=(matched_ev or {}).get("created_at"),
        detail=(matched_ev or {}).get("detail") or (matched_tr or {}).get("detail"),
    )

    if case.status == "rejected":
        add(
            "rejected",
            "Rejected",
            done=True,
            active=False,
            detail=case.hitl_note,
        )
        add("dispatched", "Dispatched", done=False, skipped=True)
        add("closed", "Closed", done=False, skipped=True)
    else:
        add(
            "dispatched",
            "Dispatched",
            done=case.status in ("dispatched", "closed") or bool(case.ticket_id),
            active=case.status == "dispatched",
            detail=case.ticket_id,
        )
        add(
            "closed",
            "Closed",
            done=case.status == "closed",
            active=False,
            at=case.resolved_at.isoformat() if case.resolved_at else None,
        )

    return stages
