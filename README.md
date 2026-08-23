# Alkhidmat Relief Copilot

Multi-agent AI aid desk for relief NGOs — Alibaba Cloud AI Hackathon Pakistan 2026.

> A multi-agent AI desk that turns an aid request (Urdu/English) into a verified, routed relief ticket — with human approval for high-risk cases.

## Status

**Tier A build in progress** — LangGraph aid desk (FastAPI + Next.js 14 + Qwen).

## Product

NGO **Aid Desk SaaS** module: citizen request → LangGraph agents (Intake → Triage → Integrity → Matcher → Dispatch) → ticket with HITL supervisor for critical cases.

## Stack

| Layer | Technology |
|-------|------------|
| Orchestration | LangGraph |
| LLM | Qwen (DashScope) / mock mode |
| API | FastAPI |
| UI | Next.js 14 |
| DB | SQLite |

## Quick start

### Backend

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
pip install -r requirements.txt
copy ..\.env.example .env   # or set env vars
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000 — API expected at http://localhost:8000.

## Key docs

| Doc | Purpose |
|-----|---------|
| [docs/PRODUCT_DEFINITION.md](docs/PRODUCT_DEFINITION.md) | Product identity + Tier A/B/C |
| [AGENTS.md](AGENTS.md) | Product + workflow agents |
| [docs/HACKATHON_MASTER_PLAN.md](docs/HACKATHON_MASTER_PLAN.md) | Timeline and scope |
| [Alkhidmat_Relief_Copilot.md](Alkhidmat_Relief_Copilot.md) | Original hackathon brief |

## Repo

https://github.com/Atif1299/alkhidmat-relief-copilot

## Event

Alibaba Cloud AI Hackathon Pakistan 2026 — Alkhidmat Foundation / Bano Qabil — *AI for Pakistan's Future*
