"""API input validation tests (lab Stage 4 spirit)."""

from __future__ import annotations


def test_chat_rejects_blank_message(client):
    r = client.post("/api/v1/chat/sync", json={"message": "   "})
    assert r.status_code == 422


def test_chat_rejects_empty_message(client):
    r = client.post("/api/v1/chat/sync", json={"message": ""})
    assert r.status_code == 422


def test_chat_rejects_oversized_message(client):
    r = client.post("/api/v1/chat/sync", json={"message": "x" * 4001})
    assert r.status_code == 422


def test_chat_rejects_bad_case_id(client):
    r = client.post(
        "/api/v1/chat/sync",
        json={"message": "Need food in Township Lahore. Phone 03015550001", "case_id": "not-a-uuid"},
    )
    assert r.status_code == 422


def test_login_rejects_invalid_email(client):
    r = client.post(
        "/api/v1/auth/login",
        json={"email": "not-an-email", "password": "AidDesk!2026"},
    )
    assert r.status_code == 422


def test_login_normalizes_email_case(client):
    r = client.post(
        "/api/v1/auth/login",
        json={"email": "  Desk@AidDesk.Example  ", "password": "AidDesk!2026"},
    )
    assert r.status_code == 200, r.text
    assert r.json()["role"] == "desk"


def test_decide_rejects_bad_decision(client, auth_headers):
    r = client.post(
        "/api/v1/supervisor/00000000-0000-0000-0000-000000000001/decide",
        headers=auth_headers,
        json={"decision": "maybe"},
    )
    assert r.status_code == 422


def test_decide_rejects_oversized_note(client, auth_headers):
    r = client.post(
        "/api/v1/supervisor/00000000-0000-0000-0000-000000000001/decide",
        headers=auth_headers,
        json={"decision": "approve", "note": "n" * 1001},
    )
    assert r.status_code == 422


def test_anonymous_cases_forbidden(client):
    r = client.get("/api/v1/cases")
    assert r.status_code == 401


def test_status_rejects_blank_ticket(client):
    r = client.post("/api/v1/public/status", json={"ticket_id": "   ", "phone": "03001234567"})
    assert r.status_code == 422


def test_status_rejects_short_phone(client):
    r = client.post("/api/v1/public/status", json={"ticket_id": "AKD-SEED-001", "phone": "123"})
    assert r.status_code == 422
