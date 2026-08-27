# Architecture — Alkhidmat Relief Copilot (Tier B)

## Product

NGO **Aid Desk SaaS** module: messy Urdu/English aid request → verified, resource-matched ticket with HITL for critical/high-risk cases — plus SOP knowledge retrieval, role views, case timeline, and PDF export.

## Stack

| Layer | Choice |
|-------|--------|
| Orchestration | LangGraph (SQLite checkpointer locally; **Postgres** checkpointer on GCP) |
| LLM | DashScope Qwen (`LLM_MODE=qwen`) or deterministic mock |
| Knowledge | File SOPs → `sop_chunks` + keyword retrieval |
| API | FastAPI + SSE |
| UI | Next.js 14 App Router (demo role switcher) |
| DB | SQLite locally; **Cloud SQL Postgres** on GCP |
| PDF | reportlab |
| Deploy | **GCP Cloud Run** (project `x-saas-488416`) — see [DEPLOYMENT.md](DEPLOYMENT.md) |

## Graph (Tier B)

```
START → Intake → Triage → Knowledge → Integrity
                                          ├─ (normal) → Matcher → Dispatch → END
                                          └─ (HITL) → hitl_gate → END (pause)
                                                     resume(approve) → Matcher → Dispatch → END
                                                     resume(reject) → END
```

**Non-negotiable:** Integrity never skipped on create. Knowledge runs after Triage (category known) before Integrity.

## Tier B modules

| Capability | Implementation |
|------------|----------------|
| B8 Knowledge / light RAG | `backend/app/knowledge/sops/`, `SopChunk`, `search_sops`, `knowledge_node` |
| B9 Role views | Topbar switcher `requester\|desk\|supervisor` (localStorage); client nav gating |
| B10 Timeline | `GET /api/v1/cases/{id}/timeline` + `/cases/[id]` UI |
| B11 Lahore seed | Expanded resources/volunteers/cases + SOP index on startup |
| B12 PDF export | `GET /api/v1/cases/{id}/export.pdf` |

## Key modules

- `backend/app/agents/graph.py` — compiled graph + `run_pipeline` / `resume_after_hitl`
- `backend/app/agents/nodes.py` — Intake…Knowledge…Dispatch
- `backend/app/tools/cases.py` — case tools
- `backend/app/tools/sops.py` — SOP retrieval
- `backend/app/services/llm.py` — mock + Qwen
- `backend/app/services/pdf_export.py` — case PDF
- `frontend/app/chat` — live AgentTrace + SOP citations
- `frontend/app/cases/[id]` — timeline + export
- `frontend/app/supervisor` — HITL queue

## Cloud mapping

| Provider | Service | Role |
|----------|---------|------|
| Alibaba | DashScope / Qwen | Agent LLM |
| Alibaba | Qoder | Hackathon IDE / Skills-MCP narrative |
| **GCP** | Cloud Run `relief-api` / `relief-web` | Live product HTTPS |
| **GCP** | Cloud SQL Postgres | Cases + HITL checkpoints |
| **GCP** | Secret Manager | DashScope API key |
| Alibaba | OSS | Future doc upload (stretch) — not required for live |

**Note:** Alibaba ECS was attempted then abandoned (free trial ineligible). Hosting is GCP-only.

## Run locally

See root [README.md](../README.md). Optional: `docker compose up` (SQLite + nginx) for local prod-like smoke.

## Deploy

**Source of truth:** [DEPLOYMENT.md](DEPLOYMENT.md)

1. GCP project `x-saas-488416`, region `asia-south1`.
2. `bash deploy/gcp/03_build_and_deploy.sh` (after bootstrap).
3. Web build-arg `NEXT_PUBLIC_API_URL` = API Cloud Run URL; API `CORS_ORIGINS` = web origin.
