"""Audit logger."""

from __future__ import annotations

from typing import Any, Optional

from sqlalchemy.orm import Session

from app.db.models import CaseEvent


def log_event(
    db: Session,
    *,
    case_id: str,
    actor: str,
    event_type: str,
    detail: Optional[str] = None,
    payload: Optional[dict[str, Any]] = None,
) -> CaseEvent:
    event = CaseEvent(
        case_id=case_id,
        actor=actor,
        event_type=event_type,
        detail=detail,
        payload=payload,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def list_events(db: Session, case_id: str) -> list[dict[str, Any]]:
    rows = (
        db.query(CaseEvent)
        .filter(CaseEvent.case_id == case_id)
        .order_by(CaseEvent.created_at.asc())
        .all()
    )
    return [
        {
            "id": e.id,
            "actor": e.actor,
            "event_type": e.event_type,
            "detail": e.detail,
            "payload": e.payload,
            "created_at": e.created_at.isoformat() if e.created_at else None,
        }
        for e in rows
    ]
