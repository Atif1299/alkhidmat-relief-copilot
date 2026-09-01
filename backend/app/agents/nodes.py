"""LangGraph nodes: Intake → Triage → Knowledge → Integrity → HITL → Matcher → Dispatch."""

from __future__ import annotations

import time
import uuid
from datetime import datetime
from typing import Any, Literal

from app.agents.state import CaseState, dedupe_trace
from app.db.session import SessionLocal
from app.services import llm as llm_service
from app.services.audit import log_event
from app.tools import cases as case_tools
from app.tools import sops as sop_tools


def _now_ms() -> int:
    return int(time.time() * 1000)


def _step(agent: str, action: str, detail: str, **extra: Any) -> dict[str, Any]:
    return {"agent": agent, "action": action, "detail": detail, "ts_ms": _now_ms(), **extra}


async def intake_node(state: CaseState) -> dict[str, Any]:
    message = state["raw_message"]
    case_id = state.get("case_id") or str(uuid.uuid4())
    extracted = await llm_service.extract_with_llm(message)
    language = extracted.get("language") or "en"
    db = SessionLocal()
    try:
        case_tools.ensure_draft_case(
            db,
            case_id=case_id,
            raw_message=message,
            language=language,
            requester_name=extracted.get("requester_name"),
            requester_phone=extracted.get("requester_phone"),
            location=extracted.get("location"),
            need_summary=extracted.get("need_summary"),
            status="processing",
        )
    finally:
        db.close()
    return {
        "case_id": case_id,
        "language": language,
        "extracted": extracted,
        "started_at_ms": state.get("started_at_ms") or _now_ms(),
        "status": "processing",
        "agent_trace": [
            _step("Intake", "extract", f"lang={language}; need={str(extracted.get('need_summary', ''))[:80]}")
        ],
    }


async def triage_node(state: CaseState) -> dict[str, Any]:
    extracted = state.get("extracted") or {}
    classified = await llm_service.classify_with_llm(extracted, state["raw_message"])
    return {
        "category": classified["category"],
        "priority": classified["priority"],
        "agent_trace": [
            _step(
                "Triage",
                "classify",
                f"category={classified['category']} priority={classified['priority']}",
                rationale=classified.get("rationale"),
            )
        ],
    }


async def knowledge_node(state: CaseState) -> dict[str, Any]:
    db = SessionLocal()
    try:
        category = state.get("category") or "Other"
        extracted = state.get("extracted") or {}
        query = " ".join(
            filter(
                None,
                [
                    state.get("raw_message"),
                    extracted.get("need_summary"),
                    extracted.get("location"),
                    category,
                ],
            )
        )
        hits = sop_tools.search_sops(db, category=category, query=query, limit=3)
        titles = ", ".join(h["title"] for h in hits) if hits else "none"
        mode = (hits[0].get("retrieval_mode") if hits else "keyword") or "keyword"
        log_event(
            db,
            case_id=state["case_id"],
            actor="Knowledge",
            event_type="sop_retrieved",
            detail=titles,
            payload={"sop_hits": hits, "retrieval_mode": mode},
        )
        return {
            "sop_hits": hits,
            "agent_trace": [
                _step(
                    "Knowledge",
                    "sop_retrieved",
                    f"Retrieved {len(hits)} SOP(s) via {mode}: {titles}",
                    sop_hits=hits,
                    retrieval_mode=mode,
                )
            ],
        }
    finally:
        db.close()


async def integrity_node(state: CaseState) -> dict[str, Any]:
    db = SessionLocal()
    try:
        phone = (state.get("extracted") or {}).get("requester_phone")
        location = (state.get("extracted") or {}).get("location")
        similar = case_tools.search_similar_cases(db, phone=phone, location=location, hours=48)
        similar = [item for item in similar if item["id"] != state.get("case_id")]

        risk = 0.1
        reasons: list[str] = []
        duplicate = False
        if similar and phone:
            duplicate = True
            risk = 0.85
            reasons.append(f"Duplicate phone ({len(similar)} recent)")
        if state.get("priority") == "critical":
            risk = max(risk, 0.9)
            reasons.append("Critical priority")
        if not phone:
            risk = max(risk, 0.35)
            reasons.append("Missing phone")

        requires_hitl = bool(duplicate or state.get("priority") == "critical" or risk >= 0.75)
        integrity = {
            "risk_score": risk,
            "duplicate_flag": duplicate,
            "reasons": reasons,
            "similar_cases": similar[:3],
        }
        if requires_hitl:
            case_tools.escalate_to_human(
                db,
                case_id=state["case_id"],
                reason="; ".join(reasons) or "HITL required",
            )
        else:
            log_event(
                db,
                case_id=state["case_id"],
                actor="Integrity",
                event_type="risk_cleared",
                detail="No HITL required",
                payload=integrity,
            )
        return {
            "integrity": integrity,
            "requires_hitl": requires_hitl,
            "status": "pending_hitl" if requires_hitl else "processing",
            "agent_trace": [
                _step(
                    "Integrity",
                    "risk_check",
                    "; ".join(reasons) if reasons else "Clear",
                    requires_hitl=requires_hitl,
                )
            ],
        }
    finally:
        db.close()


def route_after_integrity(state: CaseState) -> Literal["hitl_gate", "matcher"]:
    if state.get("requires_hitl") and state.get("hitl_decision") not in ("approve", "reject"):
        return "hitl_gate"
    return "matcher"


async def finalize_hitl_pause(state: CaseState) -> dict[str, Any]:
    """Persist pending_hitl case when graph interrupts before hitl_gate."""
    extracted = state.get("extracted") or {}
    awaiting = _step("Supervisor", "awaiting", "Paused for human approval")
    full_trace = dedupe_trace((state.get("agent_trace") or []) + [awaiting])
    payload = {
        "language": state.get("language") or "en",
        "category": state.get("category") or "Other",
        "priority": state.get("priority") or "medium",
        "status": "pending_hitl",
        "requester_name": extracted.get("requester_name"),
        "requester_phone": extracted.get("requester_phone"),
        "location": extracted.get("location"),
        "need_summary": extracted.get("need_summary"),
        "risk_score": (state.get("integrity") or {}).get("risk_score", 0),
        "duplicate_flag": (state.get("integrity") or {}).get("duplicate_flag", False),
        "requires_hitl": True,
        "agent_trace": full_trace,
        "sop_hits": state.get("sop_hits") or [],
    }
    db = SessionLocal()
    try:
        existing = case_tools.update_case_fields(db, state["case_id"])
        if existing is None:
            case_tools.create_case(
                db,
                case_id=state["case_id"],
                raw_message=state["raw_message"],
                **payload,
            )
        else:
            case_tools.update_case_fields(db, state["case_id"], **payload)
    finally:
        db.close()
    return {
        "status": "pending_hitl",
        "agent_trace": [awaiting],
    }


async def hitl_gate_node(state: CaseState) -> dict[str, Any]:
    decision = state.get("hitl_decision")
    if decision == "approve":
        return {
            "requires_hitl": False,
            "status": "processing",
            "agent_trace": [_step("Supervisor", "approve", state.get("hitl_note") or "Approved")],
        }

    if decision == "reject":
        step = _step("Supervisor", "reject", state.get("hitl_note") or "Rejected")
        db = SessionLocal()
        try:
            case_tools.update_case_fields(
                db,
                state["case_id"],
                status="rejected",
                hitl_decision="reject",
                hitl_note=state.get("hitl_note"),
                agent_trace=dedupe_trace((state.get("agent_trace") or []) + [step]),
            )
            log_event(
                db,
                case_id=state["case_id"],
                actor="Supervisor",
                event_type="rejected",
                detail=state.get("hitl_note"),
            )
        finally:
            db.close()
        return {"status": "rejected", "agent_trace": [step]}

    return await finalize_hitl_pause(state)


def route_after_hitl(state: CaseState) -> Literal["matcher", "__end__"]:
    if state.get("hitl_decision") == "approve":
        return "matcher"
    return "__end__"


async def matcher_node(state: CaseState) -> dict[str, Any]:
    db = SessionLocal()
    try:
        category = state.get("category") or "Other"
        location = (state.get("extracted") or {}).get("location") or ""
        area = location.split(",")[0].strip() if location else None
        matched = case_tools.list_resources(db, category=category, area=area)
        if not matched:
            matched = case_tools.list_resources(db, category=category)
        if not matched:
            matched = case_tools.list_resources(db)
        # Light SOP hint: prefer names mentioned in retrieved SOP excerpts
        sop_text = " ".join(
            f"{h.get('title', '')} {h.get('excerpt', '')}".lower()
            for h in (state.get("sop_hits") or [])
        )
        if sop_text and matched:
            boosted = [
                r
                for r in matched
                if any(token in sop_text for token in r["name"].lower().split() if len(token) > 3)
            ]
            if boosted:
                rest = [r for r in matched if r not in boosted]
                matched = boosted + rest
        matched = matched[:3]
        volunteer = case_tools.assign_volunteer(db, category=category, area=area)
        log_event(
            db,
            case_id=state["case_id"],
            actor="Matcher",
            event_type="resources_matched",
            detail=f"{len(matched)} resources",
            payload={"matched": matched, "volunteer": volunteer},
        )
        vol_name = volunteer["name"] if volunteer else "none"
        return {
            "matched_resources": matched,
            "volunteer": volunteer,
            "agent_trace": [_step("Matcher", "match", f"Matched {len(matched)}; volunteer={vol_name}")],
        }
    finally:
        db.close()


async def dispatch_node(state: CaseState) -> dict[str, Any]:
    db = SessionLocal()
    try:
        extracted = state.get("extracted") or {}
        matched = state.get("matched_resources") or []
        volunteer = state.get("volunteer")
        started = state.get("started_at_ms") or _now_ms()
        elapsed = _now_ms() - started
        integrity = state.get("integrity") or {}
        status = "dispatched"

        fields = {
            "language": state.get("language") or "en",
            "category": state.get("category") or "Other",
            "priority": state.get("priority") or "medium",
            "status": status,
            "requester_name": extracted.get("requester_name"),
            "requester_phone": extracted.get("requester_phone"),
            "location": extracted.get("location"),
            "need_summary": extracted.get("need_summary"),
            "risk_score": integrity.get("risk_score", 0),
            "duplicate_flag": integrity.get("duplicate_flag", False),
            "requires_hitl": False,
            "hitl_decision": state.get("hitl_decision"),
            "hitl_note": state.get("hitl_note"),
            "matched_resource_id": matched[0]["id"] if matched else None,
            "volunteer_id": volunteer["id"] if volunteer else None,
            "sop_hits": state.get("sop_hits") or [],
            "time_to_ticket_ms": elapsed,
        }

        existing = case_tools.update_case_fields(db, state["case_id"])
        if existing is None:
            result = case_tools.create_case(
                db,
                case_id=state["case_id"],
                raw_message=state["raw_message"],
                agent_trace=state.get("agent_trace") or [],
                **fields,
            )
            ticket_id = result.get("ticket_id")
        else:
            ticket_id = existing.ticket_id
            if not ticket_id:
                ticket_id = f"AKD-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
            case_tools.update_case_fields(
                db,
                state["case_id"],
                ticket_id=ticket_id,
                agent_trace=state.get("agent_trace"),
                **fields,
            )

        resource_name = matched[0]["name"] if matched else "queue"
        vol_name = volunteer["name"] if volunteer else "assigning"
        msg = f"Ticket {ticket_id} created. Matched: {resource_name}. Volunteer: {vol_name}."
        case_tools.send_status_message(
            db,
            case_id=state["case_id"],
            phone=extracted.get("requester_phone"),
            text=msg,
        )
        step = _step("Dispatch", "ticket_created", msg, ticket_id=ticket_id, status=status)
        final_trace = dedupe_trace((state.get("agent_trace") or []) + [step])
        case_tools.update_case_fields(
            db,
            state["case_id"],
            agent_trace=final_trace,
            status=status,
            ticket_id=ticket_id,
        )
        return {
            "ticket_id": ticket_id,
            "status": status,
            "notification": msg,
            "agent_trace": [step],
        }
    finally:
        db.close()
