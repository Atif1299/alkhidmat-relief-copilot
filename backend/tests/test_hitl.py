"""Supervisor decisions: approve, reject, no-checkpoint cases, repeat and unknown."""

from __future__ import annotations

import random
import uuid
from datetime import datetime

from app.db.models import Case
from app.db.session import SessionLocal


def _phone() -> str:
    return "0301" + "".join(random.choice("0123456789") for _ in range(7))


def _critical_case(client, headers) -> dict:
    r = client.post(
        "/api/v1/chat/sync",
        headers=headers,
        json={"message": f"Chest pain, need ambulance, Johar Town. Phone {_phone()}"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "pending_hitl"
    return data


def _decide(client, headers, case_id: str, decision: str):
    return client.post(
        f"/api/v1/supervisor/{case_id}/decide",
        headers=headers,
        json={"decision": decision, "note": "test decision"},
    )


def _agents(trace: list[dict]) -> list[str]:
    return [step.get("agent") for step in trace or []]


def test_reject_closes_case_without_dispatch(client, auth_headers):
    data = _critical_case(client, auth_headers)
    r = _decide(client, auth_headers, data["case_id"], "reject")
    assert r.status_code == 200, r.text
    assert r.json()["status"] == "rejected"

    case = client.get(f"/api/v1/cases/{data['case_id']}", headers=auth_headers).json()
    assert case["status"] == "rejected"
    assert case["hitl_decision"] == "reject"
    assert case["volunteer_id"] is None
    assert "Matcher" not in _agents(case["agent_trace"])
    assert "Dispatch" not in _agents(case["agent_trace"])

    status = client.post(
        "/api/v1/public/status",
        json={"ticket_id": data["ticket_id"], "phone": case["requester_phone"]},
    ).json()
    assert status["status"] == "rejected"


def test_approve_resumes_without_rerunning_pipeline(client, auth_headers):
    data = _critical_case(client, auth_headers)
    r = _decide(client, auth_headers, data["case_id"], "approve")
    assert r.status_code == 200, r.text
    assert r.json()["status"] == "dispatched"

    case = client.get(f"/api/v1/cases/{data['case_id']}", headers=auth_headers).json()
    agents = _agents(case["agent_trace"])
    assert case["status"] == "dispatched"
    assert case["ticket_id"] == data["ticket_id"]
    assert case["matched_resource_id"]
    assert agents.count("Intake") == 1
    assert agents.index("Supervisor") < agents.index("Matcher") < agents.index("Dispatch")


def test_case_without_checkpoint_can_be_decided(client, auth_headers):
    """Seeded cases are written straight to the DB and have no paused graph."""
    case_id = str(uuid.uuid4())
    db = SessionLocal()
    try:
        db.add(
            Case(
                id=case_id,
                ticket_id=f"AKD-TEST-{uuid.uuid4().hex[:6].upper()}",
                raw_message="Chest pain, need ambulance, Johar Town.",
                language="en",
                category="Medical",
                priority="critical",
                status="pending_hitl",
                requester_phone=_phone(),
                location="Johar Town Lahore",
                risk_score=0.9,
                requires_hitl=True,
                agent_trace=[{"agent": "seed", "action": "preloaded"}],
                created_at=datetime.utcnow(),
            )
        )
        db.commit()
    finally:
        db.close()

    r = _decide(client, auth_headers, case_id, "approve")
    assert r.status_code == 200, r.text
    assert r.json()["status"] == "dispatched"
    case = client.get(f"/api/v1/cases/{case_id}", headers=auth_headers).json()
    assert case["status"] == "dispatched"
    assert case["volunteer_id"]


def test_second_decision_is_refused(client, auth_headers):
    data = _critical_case(client, auth_headers)
    assert _decide(client, auth_headers, data["case_id"], "reject").status_code == 200
    again = _decide(client, auth_headers, data["case_id"], "approve")
    assert again.status_code == 409
    case = client.get(f"/api/v1/cases/{data['case_id']}", headers=auth_headers).json()
    assert case["status"] == "rejected"


def test_time_to_ticket_excludes_supervisor_wait(client, auth_headers):
    data = _critical_case(client, auth_headers)
    paused = client.get(f"/api/v1/cases/{data['case_id']}", headers=auth_headers).json()
    assert paused["time_to_ticket_ms"] is not None

    # Approval must keep the pipeline time recorded at the pause, not add the wait.
    assert _decide(client, auth_headers, data["case_id"], "approve").status_code == 200
    approved = client.get(f"/api/v1/cases/{data['case_id']}", headers=auth_headers).json()
    assert approved["status"] == "dispatched"
    assert approved["time_to_ticket_ms"] == paused["time_to_ticket_ms"]


def test_metrics_average_counts_only_auto_dispatched(client, auth_headers):
    case_id = str(uuid.uuid4())
    db = SessionLocal()
    try:
        # A supervisor-reviewed case with a huge stored time must not move the average.
        db.add(
            Case(
                id=case_id,
                ticket_id=f"AKD-TEST-{uuid.uuid4().hex[:6].upper()}",
                raw_message="Old approved case",
                category="Medical",
                priority="critical",
                status="dispatched",
                hitl_decision="approve",
                time_to_ticket_ms=10**10,
                created_at=datetime.utcnow(),
            )
        )
        db.commit()
        auto = [
            c.time_to_ticket_ms
            for c in db.query(Case).all()
            if c.time_to_ticket_ms is not None and c.status == "dispatched" and not c.hitl_decision
        ]
    finally:
        db.close()
    metrics = client.get("/api/v1/metrics", headers=auth_headers).json()
    expected = int(sum(auto) / len(auto)) if auto else 0
    assert metrics["avg_time_to_ticket_ms"] == expected
    assert metrics["avg_time_to_ticket_ms"] < 10**10


def test_unknown_case_is_404(client, auth_headers):
    assert _decide(client, auth_headers, str(uuid.uuid4()), "approve").status_code == 404
