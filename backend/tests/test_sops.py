"""Knowledge retrieval: category-only citations, Urdu guide, Integrity rules, reindex."""

from __future__ import annotations

import random

from app.db.models import SopChunk
from app.db.session import SessionLocal
from app.tools import sops as sop_tools


def _phone() -> str:
    return "0301" + "".join(random.choice("0123456789") for _ in range(7))


def _run(client, headers, message: str) -> dict:
    r = client.post("/api/v1/chat/sync", headers=headers, json={"message": message})
    assert r.status_code == 200
    return r.json()


def _files(data: dict) -> list[str]:
    return [h.get("source_file") for h in data.get("sop_hits") or []]


def _categories(data: dict) -> set[str]:
    return {h.get("category") for h in data.get("sop_hits") or []}


def test_english_food_cites_only_food_sops(client, auth_headers):
    data = _run(client, auth_headers, f"Need a food ration pack for my household in Gulberg. Phone {_phone()}")
    assert data["category"] == "Food"
    assert data["sop_hits"]
    assert _categories(data) == {"Food"}


def test_urdu_request_adds_phrase_guide(client, auth_headers):
    data = _run(
        client,
        auth_headers,
        f"Flood ke baad khane ki zaroorat hai, Township Lahore. Phone {_phone()}",
    )
    assert data["language"] == "ur"
    assert _categories(data) == {"Food", "Language"}
    assert "language_urdu_phrases.md" in _files(data)


def test_medicine_request_ranks_medicine_sop_first(client, auth_headers):
    data = _run(
        client,
        auth_headers,
        f"Need medical help, insulin for diabetes is running out, Model Town. Phone {_phone()}",
    )
    assert data["category"] == "Medical"
    assert _files(data)[0] == "medical_medicines.md"


def test_critical_medical_cites_emergency_and_escalation(client, auth_headers):
    data = _run(client, auth_headers, f"Chest pain, need ambulance, Johar Town. Phone {_phone()}")
    assert data["status"] == "pending_hitl"
    files = _files(data)
    assert "medical_emergency.md" in files
    assert "integrity_escalation.md" in files
    assert _categories(data) <= {"Medical", "Integrity"}


def test_duplicate_cites_duplicate_rule(client, auth_headers):
    phone = _phone()
    _run(client, auth_headers, f"Need food ration pack, Township Lahore. Phone {phone}")
    data = _run(client, auth_headers, f"Need food ration pack again, Township Lahore. Phone {phone}")
    assert data["status"] == "pending_hitl"
    assert "integrity_duplicates.md" in _files(data)
    assert _categories(data) <= {"Food", "Integrity"}


def test_other_category_cites_nothing(client, auth_headers):
    data = _run(client, auth_headers, f"I want to volunteer this weekend. Phone {_phone()}")
    assert data["category"] == "Other"
    assert not data.get("sop_hits")


def test_reindexes_when_sop_files_change(tmp_path, monkeypatch):
    sop = "# {title}\n\n**Category:** Food  \n**Keywords:** food\n\n## Purpose\n\nTest.\n"
    (tmp_path / "a.md").write_text(sop.format(title="First title"), encoding="utf-8")
    (tmp_path / "b.md").write_text(sop.format(title="Second"), encoding="utf-8")
    monkeypatch.setattr(sop_tools, "SOPS_DIR", tmp_path)
    db = SessionLocal()
    try:
        assert sop_tools.index_sops_from_files(db, embed=False) == 2
        (tmp_path / "a.md").write_text(sop.format(title="Edited title"), encoding="utf-8")
        assert sop_tools.index_sops_from_files(db, embed=False) == 2
        titles = {c.title for c in db.query(SopChunk).all()}
        assert titles == {"Edited title", "Second"}
    finally:
        monkeypatch.undo()
        sop_tools.index_sops_from_files(db, embed=False)
        db.close()
