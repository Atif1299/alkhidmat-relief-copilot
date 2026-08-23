"""Alkhidmat Relief Copilot API — Tier A Aid Desk."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings

app = FastAPI(
    title="Alkhidmat Relief Copilot",
    description="Multi-agent NGO aid desk — Intake → Triage → Integrity → Matcher → Dispatch",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok", "service": "alkhidmat-relief-copilot", "tier": "A"}
