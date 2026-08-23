"""E2E scenarios: happy path, duplicate, escalation."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.db.seed import DUPLICATE_DEMO_PHONE
from app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_happy_path_food():
    r = client.post(
        "/api/v1/chat/sync",
        json={
            "message": "Flood ke baad khane ki zaroorat hai, Township Lahore, family of 5. Phone 03013334445"
        },
    )
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "dispatched"
    assert data["category"] == "Food"
    assert data["ticket_id"]
    agents = [s["agent"] for s in data["agent_trace"]]
    assert agents == ["Intake", "Triage", "Integrity", "Matcher", "Dispatch"]


def test_duplicate_phone_escalates():
    r = client.post(
        "/api/v1/chat/sync",
        json={
            "message": f"Need food packs again Township Lahore. Phone {DUPLICATE_DEMO_PHONE}"
        },
    )
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "pending_hitl"
    assert data["requires_hitl"] is True
    assert data["integrity"]["duplicate_flag"] is True


def test_critical_hitl_then_approve():
    r = client.post(
        "/api/v1/chat/sync",
        json={"message": "Chest pain, need ambulance, Johar Town. Phone 03014445556"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "pending_hitl"
    assert data["priority"] == "critical"
    case_id = data["case_id"]

    queue = client.get("/api/v1/supervisor/queue")
    assert queue.status_code == 200
    assert any(item["id"] == case_id for item in queue.json())

    decided = client.post(
        f"/api/v1/supervisor/{case_id}/decide",
        json={"decision": "approve", "note": "Medical verified"},
    )
    assert decided.status_code == 200
    body = decided.json()
    assert body["status"] == "dispatched"
    assert body["ticket_id"]


def test_metrics():
    r = client.get("/api/v1/metrics")
    assert r.status_code == 200
    data = r.json()
    assert "cases_today" in data
    assert "avg_time_to_ticket_ms" in data
    assert "escalation_pct" in data
