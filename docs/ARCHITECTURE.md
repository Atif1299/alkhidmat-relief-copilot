# Architecture — Alkhidmat Relief Copilot (Tier 3 + Product Polish)

## Product

NGO **Aid Desk SaaS**: Urdu/English request → verified ticket with HITL — JWT staff roles, Postgres, vector SOP RAG.

**Winning signal:** Citizen and desk both know what happens next (ticket ID, match, or waiting for supervisor).

## Stack

| Layer | Choice |
|-------|--------|
| Orchestration | LangGraph + **Postgres** checkpointer (Compose / Cloud SQL) |
| LLM | DashScope Qwen |
| Knowledge | SOP files → embeddings (DashScope) → **pgvector / cosine** + keyword fallback |
| Auth | JWT (HS256) + bcrypt; roles `requester` \| `desk` \| `supervisor` |
| API | FastAPI + SSE; **guest** `POST /chat` allowed |
| UI | Next.js 14 — public landing + `/request`, staff `/login` |
| DB | **Docker Postgres + pgvector** locally; Cloud SQL on GCP |
| PDF | reportlab |
| Deploy | GCP Cloud Run — [DEPLOYMENT.md](DEPLOYMENT.md) |

**SQLite** is retired as the product target (tests may still use it).

## Public vs staff (product IA)

```mermaid
flowchart LR
  Landing["/ landing"] --> Request["/request guest"]
  Landing --> Login["/login staff"]
  Request --> Graph["LangGraph pipeline"]
  Graph --> TicketOrHITL["ticket or pending_HITL"]
  Login --> Ops["tickets dashboard supervisor"]
```

| Route | Who | Auth |
|-------|-----|------|
| `/` | Everyone | Public landing (Request aid + Staff sign in) |
| `/request` | Citizens | **No account** — anonymous chat API |
| `/login` | Desk / Supervisor | JWT |
| `/tickets`, `/dashboard`, `/supervisor`, `/cases/[id]` | Staff | JWT (role-gated) |
| `/chat` | Staff | JWT — test intake sandbox |

Staff default home after login: **`/tickets`**.

## Graph

```
START → Intake → Triage → Knowledge → Integrity
                                          ├─ (normal) → Matcher → Dispatch → END
                                          └─ (HITL) interrupt_before hitl_gate → pending_hitl
                                                     resume(approve) → Matcher → Dispatch → END
```

**Non-negotiable:** Integrity is never skipped on create. HITL when critical priority, duplicate, or high integrity risk.

Compile uses LangGraph `interrupt_before=["hitl_gate"]` so approve does **not** re-run Intake/Triage. Guest `POST /api/v1/chat` **streams each node** as SSE `agent_step` (live pipeline); `POST /chat/sync` still returns the full result (tests).

## Architecture story (judges / onboarding)

1. Citizen describes need in Urdu or English on **Request aid** (no signup).
2. The **live desk pipeline** lights each agent as it runs (green ring = in process). High-risk cases **hold on Integrity** until Supervisor approve/reject.
3. SOP citations are purpose + complete rules/phrases (not raw markdown tables).
4. Desk operators see tickets, timeline, agent trace, and PDF export.

## Tier 3 modules

| ID | Capability |
|----|------------|
| T3-13 | Compose `db` = `pgvector/pgvector:pg16` |
| T3-14 | `POST /api/v1/auth/login`, `GET /me`; API role gates |
| T3-15 | Vector `search_sops` + `retrieval_mode` in trace |
| T3-16 | Promote JWT_SECRET + vector ext to Cloud SQL |

## Demo users (password `AidDesk!2026`)

| Email | Role | UI entry |
|-------|------|----------|
| desk@aiddesk.example | desk | Staff sign in |
| supervisor@aiddesk.example | supervisor | Staff sign in |
| citizen@aiddesk.example | requester | Seeded for API tests; citizens use `/request` without login |

## Cloud mapping

| Provider | Service | Role |
|----------|---------|------|
| Alibaba | DashScope | LLM + embeddings |
| GCP | Cloud Run | Live HTTPS |
| GCP | Cloud SQL + pgvector | Cases, checkpoints, vectors |
| GCP | Secret Manager | DashScope + JWT |

## Run locally (Tier 3)

Product DB is Postgres. If Docker is available and port **5432 is free**:

```bash
docker compose up -d db
# backend/.env → DATABASE_URL=postgresql+psycopg://aiddesk:aiddesk@localhost:5432/aiddesk
cd backend && .venv\Scripts\activate && pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
cd frontend && npm run dev
```

If `5432` is already another Postgres (wrong password for `aiddesk`), either stop that container or set `DATABASE_URL=sqlite:///./data/relief.db` for a local UI preview. **pytest always uses SQLite** (`backend/tests/conftest.py`) — no Docker required.

Open http://localhost:3000 — landing. Citizens: **Request aid**. Staff: **Staff sign in**.
