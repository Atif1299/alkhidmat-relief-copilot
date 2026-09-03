"""E2E scenarios: happy path, duplicate, escalation, auth gates."""

from __future__ import annotations

import uuid

from app.db.seed import DUPLICATE_DEMO_PHONE, HITL_STATUS_DEMO_PHONE, HITL_STATUS_DEMO_TICKET


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
    assert r.json().get("tier") == "3"
    assert r.json().get("auth_required") is True


def test_anonymous_chat_allowed(client):
    """Public /request path — no JWT required for intake."""
    phone = f"0301{uuid.uuid4().hex[:7]}"
    r = client.post(
        "/api/v1/chat/sync",
        json={
            "message": f"Flood ke baad khane ki zaroorat hai, Township Lahore. Phone {phone}"
        },
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body.get("case_id")
    assert body.get("ticket_id")
    assert body.get("status") in ("dispatched", "pending_hitl")


def test_anonymous_supervisor_forbidden(client):
    r = client.get("/api/v1/supervisor/queue")
    assert r.status_code == 401
    decide = client.post(
        "/api/v1/supervisor/00000000-0000-0000-0000-000000000000/decide",
        json={"decision": "approve"},
    )
    assert decide.status_code == 401


def test_login_seeded_users(client):
    for email in (
        "citizen@aiddesk.example",
        "desk@aiddesk.example",
        "supervisor@aiddesk.example",
    ):
        r = client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": "AidDesk!2026"},
        )
        assert r.status_code == 200, r.text
        assert r.json()["access_token"]


def test_keyword_rag_retrieval_mode(client, auth_headers):
    """Without DashScope key, Knowledge uses keyword fallback."""
    phone = f"0301{uuid.uuid4().hex[:7]}"
    r = client.post(
        "/api/v1/chat/sync",
        headers=auth_headers,
        json={
            "message": f"Flood ke baad khane ki zaroorat hai, Township Lahore. Phone {phone}"
        },
    )
    assert r.status_code == 200
    hits = r.json().get("sop_hits") or []
    assert hits
    assert hits[0].get("retrieval_mode") == "keyword"


def test_citizen_cannot_decide(client, citizen_headers, auth_headers):
    phone = f"0301{uuid.uuid4().hex[:7]}"
    r = client.post(
        "/api/v1/chat/sync",
        headers=citizen_headers,
        json={"message": f"Chest pain, need ambulance, Johar Town. Phone {phone}"},
    )
    assert r.status_code == 200
    case_id = r.json()["case_id"]
    denied = client.post(
        f"/api/v1/supervisor/{case_id}/decide",
        headers=citizen_headers,
        json={"decision": "approve"},
    )
    assert denied.status_code == 403


def test_happy_path_food(client, auth_headers):
    phone = f"0301{uuid.uuid4().hex[:7]}"
    r = client.post(
        "/api/v1/chat/sync",
        headers=auth_headers,
        json={
            "message": f"Flood ke baad khane ki zaroorat hai, Township Lahore, family of 5. Phone {phone}"
        },
    )
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "dispatched"
    assert data["category"] == "Food"
    assert data["ticket_id"]
    agents = [s["agent"] for s in data["agent_trace"]]
    assert agents == ["Intake", "Triage", "Knowledge", "Integrity", "Matcher", "Dispatch"]
    assert data.get("sop_hits")
    assert data["sop_hits"][0].get("title")


def test_duplicate_phone_escalates(client, auth_headers):
    r = client.post(
        "/api/v1/chat/sync",
        headers=auth_headers,
        json={
            "message": f"Need food packs again Township Lahore. Phone {DUPLICATE_DEMO_PHONE}"
        },
    )
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "pending_hitl"
    assert data["requires_hitl"] is True
    assert data["integrity"]["duplicate_flag"] is True
    assert data["ticket_id"]
    assert str(data["ticket_id"]).startswith("AKD-")


def test_critical_hitl_then_approve(client, auth_headers):
    phone = f"0301{uuid.uuid4().hex[:7]}"
    r = client.post(
        "/api/v1/chat/sync",
        headers=auth_headers,
        json={"message": f"Chest pain, need ambulance, Johar Town. Phone {phone}"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "pending_hitl"
    assert data["priority"] == "critical"
    case_id = data["case_id"]

    queue = client.get("/api/v1/supervisor/queue", headers=auth_headers)
    assert queue.status_code == 200
    assert any(item["id"] == case_id for item in queue.json())

    decided = client.post(
        f"/api/v1/supervisor/{case_id}/decide",
        headers=auth_headers,
        json={"decision": "approve", "note": "Medical verified"},
    )
    assert decided.status_code == 200
    body = decided.json()
    assert body["status"] == "dispatched"
    assert body["ticket_id"]
    detail = client.get(f"/api/v1/cases/{case_id}", headers=auth_headers)
    agents = [s["agent"] for s in detail.json().get("agent_trace") or []]
    assert agents.count("Intake") == 1
    assert agents.count("Triage") == 1
    assert "Matcher" in agents
    assert "Dispatch" in agents


def test_metrics(client, desk_headers):
    r = client.get("/api/v1/metrics", headers=desk_headers)
    assert r.status_code == 200
    data = r.json()
    assert "cases_today" in data
    assert "avg_time_to_ticket_ms" in data
    assert "escalation_pct" in data


def test_timeline_and_pdf(client, auth_headers, desk_headers):
    phone = f"0301{uuid.uuid4().hex[:7]}"
    created = client.post(
        "/api/v1/chat/sync",
        headers=auth_headers,
        json={
            "message": f"Need food packs Township Lahore family of 3. Phone {phone}"
        },
    )
    assert created.status_code == 200
    case_id = created.json()["case_id"]
    assert created.json()["status"] == "dispatched"

    timeline = client.get(
        f"/api/v1/cases/{case_id}/timeline", headers=desk_headers
    )
    assert timeline.status_code == 200
    body = timeline.json()
    keys = [s["key"] for s in body["stages"] if s["state"] != "skipped"]
    assert "requested" in keys
    assert "knowledge" in keys
    assert "dispatched" in keys

    detail = client.get(f"/api/v1/cases/{case_id}", headers=auth_headers)
    assert detail.status_code == 200
    assert detail.json().get("sop_hits")
    assert detail.json().get("timeline")

    pdf = client.get(f"/api/v1/cases/{case_id}/export.pdf", headers=desk_headers)
    assert pdf.status_code == 200
    assert pdf.headers["content-type"].startswith("application/pdf")
    assert pdf.content[:4] == b"%PDF"


def test_public_status_match(client):
    r = client.post(
        "/api/v1/public/status",
        json={"ticket_id": "  akd-seed-001  ", "phone": "0300-123-4567"},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["ticket_id"] == "AKD-SEED-001"
    assert body["status"] == "dispatched"
    assert body["category"] == "Food"
    assert "dispatched" in body["next_action"].lower()
    assert body.get("resource_name")
    assert body.get("volunteer_name")
    assert "risk_score" not in body
    assert "hitl_note" not in body
    assert "agent_trace" not in body
    assert "raw_message" not in body
    assert "volunteer_phone" not in body
    keys = [s["key"] for s in body["timeline"]]
    assert "requested" in keys
    assert "dispatched" in keys
    assert "pending_hitl" not in keys
    dispatched = next(s for s in body["timeline"] if s["key"] == "dispatched")
    assert dispatched["state"] in ("done", "active")


def test_public_status_wrong_phone_404(client):
    r = client.post(
        "/api/v1/public/status",
        json={"ticket_id": "AKD-SEED-001", "phone": "03990000000"},
    )
    assert r.status_code == 404
    assert r.json()["detail"] == "Request not found"


def test_public_status_unknown_ticket_404(client):
    r = client.post(
        "/api/v1/public/status",
        json={"ticket_id": "AKD-NOPE-000", "phone": DUPLICATE_DEMO_PHONE},
    )
    assert r.status_code == 404
    assert r.json()["detail"] == "Request not found"


def test_public_status_hitl_waiting(client):
    r = client.post(
        "/api/v1/public/status",
        json={"ticket_id": HITL_STATUS_DEMO_TICKET, "phone": HITL_STATUS_DEMO_PHONE},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["status"] == "pending_hitl"
    assert "supervisor" in body["next_action"].lower()
    stages = {s["key"]: s["state"] for s in body["timeline"]}
    assert stages.get("pending_hitl") == "active"
    assert stages.get("dispatched") != "done"
    assert body.get("volunteer_name") is None
    details = " ".join(str(s.get("detail") or "") for s in body["timeline"])
    assert "Chest pain" not in details
    assert "0.9" not in details
