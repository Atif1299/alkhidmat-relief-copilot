"""Chat endpoint with SSE agent-step streaming."""

from __future__ import annotations

import json
import uuid

from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse

from app.agents.graph import run_pipeline
from app.schemas import ChatRequest

router = APIRouter(prefix="/api/v1", tags=["chat"])


@router.post("/chat")
async def chat(body: ChatRequest):
    case_id = body.case_id or str(uuid.uuid4())

    async def event_gen():
        result = await run_pipeline(body.message, case_id=case_id)
        for step in result.get("agent_trace") or []:
            yield {"event": "agent_step", "data": json.dumps(step, ensure_ascii=False)}
        if result.get("status") == "pending_hitl":
            yield {
                "event": "hitl_required",
                "data": json.dumps(
                    {
                        "case_id": result.get("case_id"),
                        "status": "pending_hitl",
                        "priority": result.get("priority"),
                        "integrity": result.get("integrity"),
                    },
                    ensure_ascii=False,
                ),
            }
        if result.get("ticket_id"):
            yield {
                "event": "ticket_created",
                "data": json.dumps(
                    {
                        "ticket_id": result.get("ticket_id"),
                        "status": result.get("status"),
                        "category": result.get("category"),
                        "notification": result.get("notification"),
                    },
                    ensure_ascii=False,
                ),
            }
        yield {
            "event": "done",
            "data": json.dumps(
                {
                    "case_id": result.get("case_id"),
                    "ticket_id": result.get("ticket_id"),
                    "status": result.get("status"),
                    "category": result.get("category"),
                    "priority": result.get("priority"),
                    "language": result.get("language"),
                    "requires_hitl": result.get("requires_hitl"),
                    "matched_resources": result.get("matched_resources"),
                    "volunteer": result.get("volunteer"),
                    "agent_trace": result.get("agent_trace"),
                    "notification": result.get("notification"),
                    "integrity": result.get("integrity"),
                    "sop_hits": result.get("sop_hits"),
                },
                ensure_ascii=False,
            ),
        }

    return EventSourceResponse(event_gen())


@router.post("/chat/sync")
async def chat_sync(body: ChatRequest):
    case_id = body.case_id or str(uuid.uuid4())
    result = await run_pipeline(body.message, case_id=case_id)
    return {
        "case_id": result.get("case_id"),
        "ticket_id": result.get("ticket_id"),
        "status": result.get("status"),
        "category": result.get("category"),
        "priority": result.get("priority"),
        "language": result.get("language"),
        "requires_hitl": result.get("requires_hitl"),
        "matched_resources": result.get("matched_resources"),
        "volunteer": result.get("volunteer"),
        "agent_trace": result.get("agent_trace"),
        "notification": result.get("notification"),
        "integrity": result.get("integrity"),
        "sop_hits": result.get("sop_hits"),
    }
