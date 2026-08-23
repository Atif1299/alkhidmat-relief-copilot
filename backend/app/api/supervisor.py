"""Supervisor HITL queue and decide API."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.agents.graph import resume_after_hitl
from app.db.models import Case
from app.db.session import get_db
from app.schemas import DecideRequest
from app.services.audit import log_event
from app.tools.cases import update_case_fields

router = APIRouter(prefix="/api/v1/supervisor", tags=["supervisor"])


@router.get("/queue")
def hitl_queue(db: Session = Depends(get_db)):
    rows = (
        db.query(Case)
        .filter(Case.status == "pending_hitl")
        .order_by(Case.created_at.asc())
        .all()
    )
    return [
        {
            "id": c.id,
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
async def decide(case_id: str, body: DecideRequest, db: Session = Depends(get_db)):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(404, "Case not found")
    if case.status != "pending_hitl":
        raise HTTPException(400, f"Case is not pending HITL (status={case.status})")

    update_case_fields(db, case_id, hitl_decision=body.decision, hitl_note=body.note)
    log_event(
        db,
        case_id=case_id,
        actor="Supervisor",
        event_type=body.decision,
        detail=body.note,
    )
    result = await resume_after_hitl(case_id, body.decision, body.note)
    return {
        "case_id": case_id,
        "decision": body.decision,
        "status": result.get("status"),
        "ticket_id": result.get("ticket_id"),
        "agent_trace": result.get("agent_trace"),
        "notification": result.get("notification"),
    }
