"""Chat endpoint with SSE agent-step streaming."""

from __future__ import annotations

import asyncio
import json
import uuid

from fastapi import APIRouter, HTTPException
from sse_starlette.sse import EventSourceResponse

from app.agents.graph import run_pipeline, stream_pipeline
from app.deps.auth import OptionalChatUser
from app.schemas import ChatRequest
from app.services.phone import message_with_phone

router = APIRouter(prefix="/api/v1", tags=["chat"])


def _intake(body: ChatRequest) -> tuple[str, str]:
    """A request needs a reachable mobile before the agents run."""
    try:
        return message_with_phone(body.message, body.phone)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc


@router.post("/chat")
async def chat(body: ChatRequest, _user: OptionalChatUser):
    case_id = body.case_id or str(uuid.uuid4())
    message, phone = _intake(body)

    async def event_gen():
        result: dict = {}
        async for kind, payload in stream_pipeline(message, case_id=case_id, phone=phone):
            if kind == "agent_step":
                yield {"event": "agent_step", "data": json.dumps(payload, ensure_ascii=False)}
                await asyncio.sleep(0.45)
            elif kind == "final":
                result = payload
        if result.get("status") == "pending_hitl":
            yield {
                "event": "hitl_required",
                "data": json.dumps(
                    {
                        "case_id": result.get("case_id"),
                        "ticket_id": result.get("ticket_id"),
                        "status": "pending_hitl",
                        "priority": result.get("priority"),
                        "integrity": result.get("integrity"),
                    },
                    ensure_ascii=False,
                ),
            }
        if result.get("ticket_id") and result.get("status") == "dispatched":
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
async def chat_sync(body: ChatRequest, _user: OptionalChatUser):
    case_id = body.case_id or str(uuid.uuid4())
    message, phone = _intake(body)
    result = await run_pipeline(message, case_id=case_id, phone=phone)
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
