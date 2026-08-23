"""MCP-style tools for the Aid Desk agents."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta
from typing import Any, Optional

from sqlalchemy.orm import Session

from app.db.models import Case, Resource, Volunteer
from app.services.audit import log_event


def search_similar_cases(
    db: Session,
    phone: Optional[str] = None,
    location: Optional[str] = None,
    hours: int = 24,
) -> list[dict[str, Any]]:
    """Find recent cases that may be duplicates (phone / area)."""
    since = datetime.utcnow() - timedelta(hours=hours)
    q = db.query(Case).filter(Case.created_at >= since)
    results: list[Case] = []
    if phone:
        normalized = "".join(c for c in phone if c.isdigit())
        for c in q.all():
            if c.requester_phone and "".join(x for x in c.requester_phone if x.isdigit()) == normalized:
                results.append(c)
    elif location:
        loc = location.lower()
        results = [c for c in q.all() if c.location and loc in c.location.lower()]
    else:
        results = q.limit(5).all()

    return [
        {
            "id": c.id,
            "ticket_id": c.ticket_id,
            "category": c.category,
            "status": c.status,
            "phone": c.requester_phone,
            "location": c.location,
            "created_at": c.created_at.isoformat() if c.created_at else None,
        }
        for c in results
    ]


def list_resources(
    db: Session,
    category: Optional[str] = None,
    city: str = "Lahore",
    area: Optional[str] = None,
) -> list[dict[str, Any]]:
    """List active inventory / camps / blood banks."""
    q = db.query(Resource).filter(Resource.active.is_(True), Resource.city == city)
    if category:
        q = q.filter(Resource.category == category)
    resources = q.all()
    if area:
        area_l = area.lower()
        # Prefer area match but fall back to all in category
        area_matched = [r for r in resources if area_l in r.area.lower()]
        if area_matched:
            resources = area_matched
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


def create_case(
    db: Session,
    *,
    case_id: str,
    raw_message: str,
    language: str,
    category: str,
    priority: str,
    status: str,
    requester_name: Optional[str] = None,
    requester_phone: Optional[str] = None,
    location: Optional[str] = None,
    need_summary: Optional[str] = None,
    risk_score: float = 0.0,
    duplicate_flag: bool = False,
    requires_hitl: bool = False,
    matched_resource_id: Optional[str] = None,
    volunteer_id: Optional[str] = None,
    agent_trace: Optional[list] = None,
    ticket_id: Optional[str] = None,
    time_to_ticket_ms: Optional[int] = None,
) -> dict[str, Any]:
    """Persist a case / ticket."""
    if not ticket_id and status in ("open", "dispatched"):
        ticket_id = f"AKD-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

    case = Case(
        id=case_id,
        ticket_id=ticket_id,
        raw_message=raw_message,
        language=language,
        category=category,
        priority=priority,
        status=status,
        requester_name=requester_name,
        requester_phone=requester_phone,
        location=location,
        need_summary=need_summary,
        risk_score=risk_score,
        duplicate_flag=duplicate_flag,
        requires_hitl=requires_hitl,
        matched_resource_id=matched_resource_id,
        volunteer_id=volunteer_id,
        agent_trace=agent_trace or [],
        time_to_ticket_ms=time_to_ticket_ms,
    )
    db.add(case)
    db.commit()
    db.refresh(case)
    log_event(db, case_id=case.id, actor="dispatch", event_type="case_created", detail=f"status={status}")
    return {
        "id": case.id,
        "ticket_id": case.ticket_id,
        "status": case.status,
        "category": case.category,
        "priority": case.priority,
    }


def assign_volunteer(
    db: Session,
    *,
    category: Optional[str] = None,
    area: Optional[str] = None,
) -> Optional[dict[str, Any]]:
    """Pick an available volunteer, preferring skill/area match."""
    volunteers = db.query(Volunteer).filter(Volunteer.available.is_(True)).all()
    if not volunteers:
        return None

    scored: list[tuple[int, Volunteer]] = []
    for v in volunteers:
        score = 0
        skills = v.skills or []
        if category and category in skills:
            score += 2
        if area and area.lower() in (v.area or "").lower():
            score += 1
        scored.append((score, v))
    scored.sort(key=lambda x: x[0], reverse=True)
    best = scored[0][1]
    return {
        "id": best.id,
        "name": best.name,
        "phone": best.phone,
        "skills": best.skills,
        "area": best.area,
    }


def escalate_to_human(
    db: Session,
    *,
    case_id: str,
    reason: str,
) -> dict[str, Any]:
    """Mark case as needing supervisor (HITL)."""
    case = db.query(Case).filter(Case.id == case_id).first()
    if case:
        case.requires_hitl = True
        case.status = "pending_hitl"
        db.commit()
    log_event(
        db,
        case_id=case_id,
        actor="integrity",
        event_type="escalated_to_human",
        detail=reason,
    )
    return {"case_id": case_id, "status": "pending_hitl", "reason": reason}


def send_status_message(
    db: Session,
    *,
    case_id: str,
    phone: Optional[str],
    text: str,
) -> dict[str, Any]:
    """Stub notifier — logs confirmation instead of SMS/WhatsApp."""
    log_event(
        db,
        case_id=case_id,
        actor="notify",
        event_type="status_message",
        detail=text,
        payload={"phone": phone, "channel": "stub"},
    )
    return {"sent": True, "channel": "stub", "phone": phone, "text": text}


def update_case_fields(db: Session, case_id: str, **fields: Any) -> Optional[Case]:
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        return None
    for k, v in fields.items():
        if hasattr(case, k) and v is not None:
            setattr(case, k, v)
    case.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(case)
    return case
