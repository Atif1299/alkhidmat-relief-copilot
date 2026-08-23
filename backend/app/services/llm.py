"""LLM service: mock heuristics or DashScope Qwen."""

from __future__ import annotations

import json
import re
from typing import Any

import httpx

from app.config import settings


def _parse_json(text: str) -> dict[str, Any]:
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]*\}", text)
        if not match:
            raise
        return json.loads(match.group(0))


def mock_extract(message: str) -> dict[str, Any]:
    lower = message.lower()
    urdu = ["کی", "ہے", "میں", "ضرورت", "کھانے", "امبولنس", "خاندان"]
    language = "ur" if any(m in message for m in urdu) or "zaroorat" in lower else "en"

    category = "Other"
    if any(k in lower for k in ["food", "khana", "khane", "ration", "کھان"]):
        category = "Food"
    if any(k in lower for k in ["shelter", "camp", "rehne", "ghar"]):
        category = "Shelter"
    if any(k in lower for k in ["blood", "khoon"]):
        category = "Blood"
    if any(k in lower for k in ["school", "education", "kitab"]):
        category = "Education"
    if any(k in lower for k in ["chest", "pain", "ambulance", "medical", "hospital", "doctor", "امبولنس"]):
        category = "Medical"

    priority = "medium"
    if any(k in lower for k in ["chest", "ambulance", "critical", "emergency", "dying", "unconscious"]):
        priority = "critical"
        category = "Medical"
    elif any(k in lower for k in ["urgent", "foran", "jaldi"]):
        priority = "high"

    phone_match = re.search(r"03\d{9}", re.sub(r"[\s-]", "", message))
    phone = phone_match.group(0) if phone_match else None

    location = "Lahore"
    for area in ["Township", "Johar Town", "Johar", "Gulberg", "Model Town", "Raiwind", "Garden Town"]:
        if area.lower() in lower or area in message:
            location = f"{area}, Lahore"
            break

    name = "Citizen"
    name_match = re.search(r"(?:name|naam)[:\s]+([A-Za-z\u0600-\u06FF ]{2,40})", message, re.I)
    if name_match:
        name = name_match.group(1).strip()

    return {
        "language": language,
        "need_summary": message[:240],
        "location": location,
        "requester_phone": phone,
        "requester_name": name,
        "category_hint": category,
        "priority_hint": priority,
    }


def mock_classify(extracted: dict[str, Any], _message: str) -> dict[str, Any]:
    return {
        "category": extracted.get("category_hint") or "Other",
        "priority": extracted.get("priority_hint") or "medium",
        "rationale": "Mock keyword triage",
    }


async def call_qwen(system: str, user: str) -> str:
    if not settings.dashscope_api_key:
        raise RuntimeError("DASHSCOPE_API_KEY not set")
    url = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.dashscope_api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": settings.dashscope_model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": 0.2,
    }
    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]


async def extract_with_llm(message: str) -> dict[str, Any]:
    if settings.llm_mode == "mock" or not settings.dashscope_api_key:
        return mock_extract(message)
    from app.agents.prompts import INTAKE_SYSTEM_EN

    data = _parse_json(await call_qwen(INTAKE_SYSTEM_EN, message))
    base = mock_extract(message)
    base.update({k: v for k, v in data.items() if v})
    return base


async def classify_with_llm(extracted: dict[str, Any], message: str) -> dict[str, Any]:
    if settings.llm_mode == "mock" or not settings.dashscope_api_key:
        return mock_classify(extracted, message)
    from app.agents.prompts import TRIAGE_SYSTEM

    user = f"Message: {message}\nExtracted: {json.dumps(extracted, ensure_ascii=False)}"
    data = _parse_json(await call_qwen(TRIAGE_SYSTEM, user))
    return {
        "category": data.get("category") or extracted.get("category_hint") or "Other",
        "priority": data.get("priority") or extracted.get("priority_hint") or "medium",
        "rationale": data.get("rationale") or "",
    }
