"""A request needs a reachable Pakistani mobile before the agents run."""

from __future__ import annotations

import random

import pytest

from app.services.phone import PHONE_INVALID, PHONE_REQUIRED, find_mobile, message_with_phone


def _digits(n: int) -> str:
    return "".join(random.choice("0123456789") for _ in range(n))


@pytest.mark.parametrize(
    "text, expected",
    [
        ("Phone 03001234567", "03001234567"),
        ("call 0300-1234567 please", "03001234567"),
        ("+92 300 1234567", "03001234567"),
        ("0092 321 7654321", "03217654321"),
        ("923451112233", "03451112233"),
        ("no number here", None),
        ("042-35789012 is a landline", None),
        ("0300123456", None),  # one digit short
    ],
)
def test_find_mobile(text, expected):
    assert find_mobile(text) == expected


def test_message_with_phone_rules():
    with pytest.raises(ValueError, match="mobile number"):
        message_with_phone("Need food in Township", None)
    with pytest.raises(ValueError, match="Pakistani mobile"):
        message_with_phone("Need food in Township", "12345")
    message, phone = message_with_phone("Need food in Township", "0300 111 2233")
    assert phone == "03001112233" and message.endswith("Phone 03001112233")
    # The field wins over a different number in the text.
    _, phone = message_with_phone("My neighbour is 03215556677", "03009998877")
    assert phone == "03009998877"


def test_chat_without_phone_is_refused(client):
    r = client.post("/api/v1/chat/sync", json={"message": "Need food packs in Township Lahore"})
    assert r.status_code == 422
    assert r.json()["detail"] == PHONE_REQUIRED


def test_chat_with_invalid_phone_field_is_refused(client):
    r = client.post("/api/v1/chat/sync", json={"message": "Need food in Gulberg", "phone": "12345"})
    assert r.status_code == 422
    assert r.json()["detail"] == PHONE_INVALID


def test_phone_field_is_used_and_status_lookup_works(client, auth_headers):
    phone = "0300" + _digits(7)
    spaced = f"{phone[:4]} {phone[4:]}"
    r = client.post(
        "/api/v1/chat/sync",
        json={"message": "Need a food ration pack, Gulberg Lahore. Neighbour 03219990000", "phone": spaced},
    )
    assert r.status_code == 200, r.text
    data = r.json()
    case = client.get(f"/api/v1/cases/{data['case_id']}", headers=auth_headers).json()
    assert case["requester_phone"] == phone
    assert phone in case["raw_message"]
    status = client.post("/api/v1/public/status", json={"ticket_id": data["ticket_id"], "phone": phone})
    assert status.status_code == 200


def test_international_format_in_message_is_normalised(client, auth_headers):
    local = "0333" + _digits(7)
    r = client.post(
        "/api/v1/chat/sync",
        json={"message": f"Need school kits, Township Lahore. Call +92 {local[1:4]} {local[4:]}"},
    )
    assert r.status_code == 200, r.text
    case = client.get(f"/api/v1/cases/{r.json()['case_id']}", headers=auth_headers).json()
    assert case["requester_phone"] == local


def test_stream_endpoint_also_requires_phone(client):
    r = client.post("/api/v1/chat", json={"message": "Need shelter in Raiwind"})
    assert r.status_code == 422
    assert r.json()["detail"] == PHONE_REQUIRED
