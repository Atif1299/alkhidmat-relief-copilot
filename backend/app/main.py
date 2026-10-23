"""Alkhidmat Relief Copilot API — Tier 3 Production Hardening."""

from __future__ import annotations

import sys

# psycopg async + LangGraph Postgres checkpointer need SelectorEventLoop on Windows
if sys.platform == "win32":
    import asyncio

    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.agents.graph import close_graph, init_graph
from app.api import auth, cases, chat, metrics, public, supervisor
from app.config import settings
from app.db.seed import run_seed
from app.db.session import init_db


logger = logging.getLogger("uvicorn.error")

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

class JsonServerErrors:
    """Turn unhandled errors into a JSON 500 inside the CORS layer.

    Starlette's default 500 is produced outside CORSMiddleware, so the browser
    sees a missing CORS header and reports "Failed to fetch" instead of the
    error. Registered before CORS so CORS wraps it.
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        started = False

        async def send_tracking(message):
            nonlocal started
            if message["type"] == "http.response.start":
                started = True
            await send(message)

        try:
            await self.app(scope, receive, send_tracking)
        except Exception:
            if started:
                raise
            logger.exception("Unhandled error on %s %s", scope.get("method"), scope.get("path"))
            response = JSONResponse({"detail": "Internal server error"}, status_code=500)
            await response(scope, receive, send)


app.add_middleware(JsonServerErrors)
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
app.include_router(public.router)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "alkhidmat-relief-copilot",
        "tier": "3",
        "auth_required": not settings.auth_disabled,
        "db": "postgres" if settings.is_postgres else "sqlite",
    }
