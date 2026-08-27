"""Cases list/detail/timeline/PDF API."""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.db.models import Case
from app.db.session import get_db
from app.deps.auth import RequireDesk, RequireRequester
from app.services.audit import list_events
from app.services.pdf_export import build_case_pdf
from app.services.timeline import build_timeline

router = APIRouter(prefix="/api/v1/cases", tags=["cases"])


def serialize_case(case: Case) -> dict:
    return {
        "id": case.id,
        "ticket_id": case.ticket_id,
        "raw_message": case.raw_message,
        "language": case.language,
        "category": case.category,
        "priority": case.priority,
        "status": case.status,
        "requester_name": case.requester_name,
        "requester_phone": case.requester_phone,
        "location": case.location,
        "need_summary": case.need_summary,
        "risk_score": case.risk_score,
        "duplicate_flag": case.duplicate_flag,
        "requires_hitl": case.requires_hitl,
        "hitl_decision": case.hitl_decision,
        "hitl_note": case.hitl_note,
        "matched_resource_id": case.matched_resource_id,
        "volunteer_id": case.volunteer_id,
        "agent_trace": case.agent_trace,
        "sop_hits": case.sop_hits,
        "time_to_ticket_ms": case.time_to_ticket_ms,
        "created_at": case.created_at.isoformat() if case.created_at else None,
    }


@router.get("")
def list_cases(
    status: str | None = None,
    db: Session = Depends(get_db),
    _user: RequireDesk = ...,
):
    query = db.query(Case).order_by(Case.created_at.desc())
    if status:
        query = query.filter(Case.status == status)
    return [serialize_case(c) for c in query.limit(100).all()]


@router.get("/{case_id}")
def get_case(
    case_id: str,
    db: Session = Depends(get_db),
    _user: RequireRequester = ...,
):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(404, "Case not found")
    data = serialize_case(case)
    data["events"] = list_events(db, case_id)
    data["timeline"] = build_timeline(case, data["events"])
    return data


@router.get("/{case_id}/timeline")
def get_timeline(
    case_id: str,
    db: Session = Depends(get_db),
    _user: RequireDesk = ...,
):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(404, "Case not found")
    events = list_events(db, case_id)
    return {
        "case_id": case_id,
        "ticket_id": case.ticket_id,
        "status": case.status,
        "stages": build_timeline(case, events),
        "events": events,
    }


@router.get("/{case_id}/export.pdf")
def export_case_pdf(
    case_id: str,
    db: Session = Depends(get_db),
    _user: RequireDesk = ...,
):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(404, "Case not found")
    data = serialize_case(case)
    events = list_events(db, case_id)
    timeline = build_timeline(case, events)
    pdf_bytes = build_case_pdf(data, timeline=timeline, events=events)
    filename = f"{case.ticket_id or case.id}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
