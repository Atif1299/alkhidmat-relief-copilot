"""Supervisor HITL queue and decide API."""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.agents.graph import resume_after_hitl
from app.db.models import Case
from app.db.session import get_db
from app.deps.auth import RequireSupervisor
from app.schemas import DecideRequest
from app.services.audit import log_event

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/supervisor", tags=["supervisor"])


def _parse_case_id(case_id: str) -> str:
    try:
        return str(UUID(case_id))
    except ValueError as exc:
        raise HTTPException(422, "case_id must be a valid UUID") from exc


@router.get("/queue")
def hitl_queue(db: Session = Depends(get_db), _user: RequireSupervisor = ...):
    rows = (
        db.query(Case)
        .filter(Case.status == "pending_hitl")
        .order_by(Case.created_at.asc())
        .all()
    )
    return [
        {
            "id": c.id,
            "ticket_id": c.ticket_id,
            "raw_message": c.raw_message,
            "category": c.category,
            "priority": c.priority,
            "location": c.location,
            "requester_phone": c.requester_phone,
            "risk_score": c.risk_score,
            "duplicate_flag": c.duplicate_flag,
            "agent_trace": c.agent_trace,
            "created_at": c.created_at.isoformat() if c.created_at else None,
        }
        for c in rows
    ]


@router.post("/{case_id}/decide")
async def decide(
    case_id: str,
    body: DecideRequest,
    db: Session = Depends(get_db),
    _user: RequireSupervisor = ...,
):
    case_id = _parse_case_id(case_id)
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(404, "Case not found")
    if case.status != "pending_hitl":
        raise HTTPException(409, f"Case was already decided (status={case.status})")

    # Apply the decision first so a failure leaves the case untouched and pending.
    try:
        result = await resume_after_hitl(case_id, body.decision, body.note)
    except Exception as exc:
        logger.exception("Supervisor decision failed for case %s", case_id)
        raise HTTPException(500, "The decision could not be applied. The case is still pending.") from exc
    log_event(
        db,
        case_id=case_id,
        actor="Supervisor",
        event_type=body.decision,
        detail=body.note,
    )
    return {
        "case_id": case_id,
        "decision": body.decision,
        "status": result.get("status"),
        "ticket_id": result.get("ticket_id"),
        "agent_trace": result.get("agent_trace"),
        "notification": result.get("notification"),
    }
