"""Citizen-facing request status — ticket + phone, no staff payload."""

from __future__ import annotations

from typing import Any, Optional

from sqlalchemy.orm import Session, joinedload

from app.db.models import Case
from app.services.audit import list_events
from app.services.timeline import citizen_timeline

NOT_FOUND = "Request not found"

_NEXT_ACTION = {
    "processing": "Received — the desk is running.",
    "pending_hitl": "Waiting for supervisor review.",
    "dispatched": "Ticket dispatched.",
    "rejected": "Not approved.",
    "closed": "Closed.",
    "open": "Received — the desk is running.",
}


def phone_digits(phone: Optional[str]) -> str:
    return "".join(c for c in (phone or "") if c.isdigit())


def lookup_public_status(db: Session, *, ticket_id: str, phone: str) -> Optional[dict[str, Any]]:
    ticket = ticket_id.strip().upper()
    digits = phone_digits(phone)
    case = (
        db.query(Case)
        .options(joinedload(Case.matched_resource), joinedload(Case.volunteer))
        .filter(Case.ticket_id == ticket)
        .first()
    )
    if case is None or phone_digits(case.requester_phone) != digits:
        return None

    resource_name = case.matched_resource.name if case.matched_resource else None
    volunteer_name = case.volunteer.name if case.volunteer else None
    events = list_events(db, case.id)
    next_action = _NEXT_ACTION.get(case.status or "", "Received — the desk is running.")
    if case.status == "dispatched":
        parts = [p for p in (resource_name, volunteer_name) if p]
        next_action = "Ticket dispatched — " + " · ".join(parts) if parts else "Ticket dispatched."

    return {
        "ticket_id": case.ticket_id,
        "status": case.status,
        "category": case.category,
        "next_action": next_action,
        "timeline": citizen_timeline(case, events),
        "resource_name": resource_name,
        "volunteer_name": volunteer_name,
    }
