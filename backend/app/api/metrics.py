"""Ops metrics for dashboard."""

from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.models import Case
from app.db.session import get_db

router = APIRouter(prefix="/api/v1/metrics", tags=["metrics"])


@router.get("")
def metrics(db: Session = Depends(get_db)):
    today = datetime.utcnow().date()
    cases = db.query(Case).all()
    cases_today = [c for c in cases if c.created_at and c.created_at.date() == today]
    with_ticket = [c for c in cases if c.time_to_ticket_ms is not None]
    avg_ms = (
        int(sum(c.time_to_ticket_ms for c in with_ticket) / len(with_ticket))
        if with_ticket
        else 0
    )
    hitl_touched = [
        c
        for c in cases
        if c.status == "pending_hitl"
        or c.hitl_decision
        or (
            c.agent_trace
            and any(step.get("agent") == "Supervisor" for step in (c.agent_trace or []))
        )
    ]
    escalation_pct = round(100.0 * len(hitl_touched) / len(cases), 1) if cases else 0.0
    by_status = db.query(Case.status, func.count(Case.id)).group_by(Case.status).all()
    by_category = db.query(Case.category, func.count(Case.id)).group_by(Case.category).all()
    return {
        "cases_today": len(cases_today),
        "cases_total": len(cases),
        "avg_time_to_ticket_ms": avg_ms,
        "escalation_pct": escalation_pct,
        "pending_hitl": len([c for c in cases if c.status == "pending_hitl"]),
        "by_status": {status or "unknown": count for status, count in by_status},
        "by_category": {category or "unknown": count for category, count in by_category},
    }
