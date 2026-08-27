# Architecture — Alkhidmat Relief Copilot (Tier 3)

## Product

NGO **Aid Desk SaaS**: Urdu/English request → verified ticket with HITL — JWT roles, Postgres, vector SOP RAG.

## Stack

| Layer | Choice |
|-------|--------|
| Orchestration | LangGraph + **Postgres** checkpointer (Compose / Cloud SQL) |
| LLM | DashScope Qwen |
| Knowledge | SOP files → embeddings (DashScope) → **pgvector / cosine** + keyword fallback |
| Auth | JWT (HS256) + bcrypt; roles `requester` \| `desk` \| `supervisor` |
| API | FastAPI + SSE |
| UI | Next.js 14 + `/login` |
| DB | **Docker Postgres + pgvector** locally; Cloud SQL on GCP |
| PDF | reportlab |
| Deploy | GCP Cloud Run — [DEPLOYMENT.md](DEPLOYMENT.md) |

**SQLite** is retired as the product target (tests may still use it).

## Graph

```
START → Intake → Triage → Knowledge → Integrity
                                          ├─ (normal) → Matcher → Dispatch → END
                                          └─ (HITL) → hitl_gate → END (pause)
                                                     resume(approve) → Matcher → Dispatch → END
```

## Tier 3 modules

| ID | Capability |
|----|------------|
| T3-13 | Compose `db` = `pgvector/pgvector:pg16` |
| T3-14 | `POST /api/v1/auth/login`, `GET /me`; API role gates |
| T3-15 | Vector `search_sops` + `retrieval_mode` in trace |
| T3-16 | Promote JWT_SECRET + vector ext to Cloud SQL |

## Demo users (password `AidDesk!2026`)

| Email | Role |
|-------|------|
| citizen@aiddesk.example | requester |
| desk@aiddesk.example | desk |
| supervisor@aiddesk.example | supervisor |

## Cloud mapping

| Provider | Service | Role |
|----------|---------|------|
| Alibaba | DashScope | LLM + embeddings |
| GCP | Cloud Run | Live HTTPS |
| GCP | Cloud SQL + pgvector | Cases, checkpoints, vectors |
| GCP | Secret Manager | DashScope + JWT |

## Run locally (Tier 3)

```bash
docker compose up -d db
# backend/.env → DATABASE_URL=postgresql+psycopg://aiddesk:aiddesk@localhost:5432/aiddesk
cd backend && .venv\Scripts\activate && pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
cd frontend && npm run dev
```

Open http://localhost:3000/login
