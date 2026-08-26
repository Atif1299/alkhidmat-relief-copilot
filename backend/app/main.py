"""Alkhidmat Relief Copilot API — Tier B Aid Desk."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import cases, chat, metrics, supervisor
from app.config import settings
from app.db.seed import run_seed
from app.db.session import init_db


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    info = run_seed()
    print(f"[startup] DB ready: {info}")
    yield


app = FastAPI(
    title="Alkhidmat Relief Copilot",
    description="Multi-agent NGO aid desk — Intake → Triage → Knowledge → Integrity → Matcher → Dispatch",
    version="0.2.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(cases.router)
app.include_router(supervisor.router)
app.include_router(metrics.router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "alkhidmat-relief-copilot", "tier": "B"}
