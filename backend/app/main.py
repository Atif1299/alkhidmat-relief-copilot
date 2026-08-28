"""Alkhidmat Relief Copilot API — Tier 3 Production Hardening."""

from __future__ import annotations

import sys

# psycopg async + LangGraph Postgres checkpointer need SelectorEventLoop on Windows
if sys.platform == "win32":
    import asyncio

    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.agents.graph import close_graph, init_graph
from app.api import auth, cases, chat, metrics, supervisor
from app.config import settings
from app.db.seed import run_seed
from app.db.session import init_db


_DEFAULT_JWT = "dev-change-me-aiddesk-jwt-secret-min-32-chars"


@asynccontextmanager
async def lifespan(_app: FastAPI):
    if settings.auth_disabled:
        print("[startup] WARNING: AUTH_DISABLED=true — API role gates are open")
    if (
        not settings.auth_disabled
        and settings.is_postgres
        and settings.jwt_secret.strip() in ("", _DEFAULT_JWT)
    ):
        print(
            "[startup] WARNING: JWT_SECRET is missing or still the default — "
            "set a strong secret before production deploy"
        )
    init_db()
    await init_graph()
    info = run_seed()
    # Seed may include demo password for local/demo — never log password hashes or JWT secrets.
    print(
        f"[startup] DB ready: resources={info.get('resources')} "
        f"users={info.get('users')} sop_chunks={info.get('sop_chunks')}"
    )
    yield
    await close_graph()


app = FastAPI(
    title="Alkhidmat Relief Copilot",
    description="Multi-agent NGO aid desk — Intake → Triage → Knowledge → Integrity → Matcher → Dispatch",
    version="0.3.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials="*" not in settings.cors_origin_list,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(cases.router)
app.include_router(supervisor.router)
app.include_router(metrics.router)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "alkhidmat-relief-copilot",
        "tier": "3",
        "auth_required": not settings.auth_disabled,
        "db": "postgres" if settings.is_postgres else "sqlite",
    }
