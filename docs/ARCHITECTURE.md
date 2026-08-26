# Architecture — Alkhidmat Relief Copilot (Tier B)

## Product

NGO **Aid Desk SaaS** module: messy Urdu/English aid request → verified, resource-matched ticket with HITL for critical/high-risk cases — plus SOP knowledge retrieval, role views, case timeline, and PDF export.

## Stack

| Layer | Choice |
|-------|--------|
| Orchestration | LangGraph (MemorySaver checkpointer for HITL resume) |
| LLM | DashScope Qwen (`LLM_MODE=qwen`) or deterministic mock |
| Knowledge | File SOPs → `sop_chunks` SQLite + keyword retrieval |
| API | FastAPI + SSE |
| UI | Next.js 14 App Router (demo role switcher) |
| DB | SQLite via SQLAlchemy |
| PDF | reportlab |

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

## Alibaba Cloud mapping

| Service | Role |
|---------|------|
| DashScope / Qwen | Agent LLM |
| Qoder | Official hackathon IDE / Skills-MCP narrative |
| ECS / Function Compute | API deploy target |
| OSS | Future doc upload (stretch) |

## Run locally

See root [README.md](../README.md).

## Deploy notes

1. Set `DASHSCOPE_API_KEY` and `LLM_MODE=qwen` for live Alibaba LLM.
2. Host API on ECS/FC; set `CORS_ORIGINS` to frontend origin.
3. Host frontend on Vercel or static host; set `NEXT_PUBLIC_API_URL`.
4. Persist SQLite volume or migrate `DATABASE_URL` to Postgres when ready.
