"""MCP-style tools for Aid Desk agents."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta
from typing import Any, Optional

from sqlalchemy.orm import Session

from app.db.models import Case, Resource, Volunteer
from app.services.audit import log_event


def search_similar_cases(
    db: Session,
    *,
    phone: Optional[str] = None,
    location: Optional[str] = None,
    hours: int = 48,
) -> list[dict[str, Any]]:
    since = datetime.utcnow() - timedelta(hours=hours)
    rows = db.query(Case).filter(Case.created_at >= since).all()
    matches: list[Case] = []
    if phone:
        digits = "".join(c for c in phone if c.isdigit())
        for case in rows:
            if case.requester_phone:
                other = "".join(c for c in case.requester_phone if c.isdigit())
                if other == digits:
                    matches.append(case)
    elif location:
        loc = location.lower()
        matches = [c for c in rows if c.location and loc in c.location.lower()]
    return [
        {
            "id": c.id,
            "ticket_id": c.ticket_id,
            "category": c.category,
            "status": c.status,
            "phone": c.requester_phone,
            "location": c.location,
        }
        for c in matches
    ]


def list_resources(
    db: Session,
    *,
    category: Optional[str] = None,
    area: Optional[str] = None,
    city: str = "Lahore",
) -> list[dict[str, Any]]:
    query = db.query(Resource).filter(Resource.active.is_(True), Resource.city == city)
    if category:
        query = query.filter(Resource.category == category)
    resources = query.all()
    if area:
        area_l = area.lower()
        preferred = [r for r in resources if area_l in r.area.lower()]
        if preferred:
            resources = preferred
    return [
        {
            "id": r.id,
            "category": r.category,
            "name": r.name,
            "city": r.city,
            "area": r.area,
            "stock": r.stock,
            "capacity": r.capacity,
            "contact": r.contact,
        }
        for r in resources
    ]


def create_case(db: Session, *, case_id: str, raw_message: str, **fields: Any) -> dict[str, Any]:
    status = fields.get("status", "processing")
    ticket_id = fields.get("ticket_id")
    if not ticket_id and status in ("open", "dispatched"):
        ticket_id = f"AKD-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        fields["ticket_id"] = ticket_id

    allowed = {k: v for k, v in fields.items() if hasattr(Case, k) and v is not None}
    case = Case(id=case_id, raw_message=raw_message, **allowed)
    db.add(case)
    db.commit()
    db.refresh(case)
    log_event(
        db,
        case_id=case.id,
        actor="Dispatch",
        event_type="case_created",
        detail=f"status={case.status} ticket={case.ticket_id}",
    )
    return {"id": case.id, "ticket_id": case.ticket_id, "status": case.status}


def update_case_fields(db: Session, case_id: str, **fields: Any) -> Optional[Case]:
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        return None
    for key, value in fields.items():
        if hasattr(case, key) and value is not None:
            setattr(case, key, value)
    case.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(case)
    return case


def assign_volunteer(
    db: Session,
    *,
    category: Optional[str] = None,
    area: Optional[str] = None,
) -> Optional[dict[str, Any]]:
    volunteers = db.query(Volunteer).filter(Volunteer.available.is_(True)).all()
    if not volunteers:
        return None
    scored: list[tuple[int, Volunteer]] = []
    for volunteer in volunteers:
        score = 0
        skills = volunteer.skills or []
        if category and category in skills:
            score += 2
        if area and area.lower() in (volunteer.area or "").lower():
            score += 1
        scored.append((score, volunteer))
    scored.sort(key=lambda item: -item[0])
    best = scored[0][1]
    return {
        "id": best.id,
        "name": best.name,
        "phone": best.phone,
        "skills": best.skills,
        "area": best.area,
    }


def escalate_to_human(db: Session, *, case_id: str, reason: str) -> dict[str, Any]:
    case = db.query(Case).filter(Case.id == case_id).first()
    if case:
        case.requires_hitl = True
        case.status = "pending_hitl"
        db.commit()
    log_event(db, case_id=case_id, actor="Integrity", event_type="escalated", detail=reason)
    return {"case_id": case_id, "status": "pending_hitl", "reason": reason}


def send_status_message(
    db: Session,
    *,
    case_id: str,
    phone: Optional[str],
    text: str,
) -> dict[str, Any]:
    log_event(
        db,
        case_id=case_id,
        actor="Notify",
        event_type="status_message",
        detail=text,
        payload={"phone": phone, "channel": "stub"},
    )
    return {"sent": True, "phone": phone, "text": text}
