# Architecture — Alkhidmat Relief Copilot (Tier A)

## Product

NGO **Aid Desk SaaS** module: messy Urdu/English aid request → verified, resource-matched ticket with HITL for critical/high-risk cases.

## Stack

| Layer | Choice |
|-------|--------|
| Orchestration | LangGraph (MemorySaver checkpointer for HITL resume) |
| LLM | DashScope Qwen (`LLM_MODE=qwen`) or deterministic mock |
| API | FastAPI + SSE |
| UI | Next.js 14 App Router |
| DB | SQLite via SQLAlchemy |

## Graph

```
START → Intake → Triage → Integrity
                              ├─ (normal) → Matcher → Dispatch → END
                              └─ (HITL) → hitl_gate → END (pause)
                                         resume(approve) → Matcher → Dispatch → END
                                         resume(reject) → END
```

**Non-negotiable:** Integrity never skipped on create.

## Key modules

- `backend/app/agents/graph.py` — compiled graph + `run_pipeline` / `resume_after_hitl`
- `backend/app/agents/nodes.py` — agent nodes
- `backend/app/tools/cases.py` — MCP-style tools
- `backend/app/services/llm.py` — mock + Qwen
- `frontend/app/chat` — live AgentTrace
- `frontend/app/supervisor` — HITL queue

## Alibaba Cloud mapping

| Service | Role |
|---------|------|
| DashScope / Qwen | Agent LLM |
| Qoder | Official hackathon IDE / Skills-MCP narrative |
| ECS / Function Compute | API deploy target |
| OSS | Future doc upload (Tier B stretch) |

## Run locally

See root [README.md](../README.md).

## Deploy notes

1. Set `DASHSCOPE_API_KEY` and `LLM_MODE=qwen` for live Alibaba LLM.
2. Host API on ECS/FC; set `CORS_ORIGINS` to frontend origin.
3. Host frontend on Vercel or static host; set `NEXT_PUBLIC_API_URL`.
4. Persist SQLite volume or migrate `DATABASE_URL` to Postgres when ready.
