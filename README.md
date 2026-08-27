# Alkhidmat Relief Copilot

Multi-agent AI aid desk for relief NGOs — Alibaba Cloud AI Hackathon Pakistan 2026.

> A multi-agent AI desk that turns an aid request (Urdu/English) into a verified, routed relief ticket — with human approval for high-risk cases.

## Status

**Tier A + Tier B complete** in product. **Deploy:** Alibaba ECS Docker Compose — see [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) (live URL pending ECS IP).

## Stack

| Layer | Technology |
|-------|------------|
| Orchestration | LangGraph (durable SQLite checkpoints) |
| LLM | Qwen (DashScope) / mock mode |
| API | FastAPI + SSE |
| UI | Next.js 14 |
| DB | SQLite |
| Live host | Alibaba ECS + nginx Compose |

## Quick start

### Backend

```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
pip install -r requirements.txt
copy ..\.env.example .env
set LLM_MODE=mock
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
copy .env.local.example .env.local
npm run dev
```

Open http://localhost:3000/chat

### Production (Docker on ECS)

```bash
cp .env.production.example .env
# set DASHSCOPE_API_KEY
docker compose up -d --build
# open http://PUBLIC_IP/chat
```

Full runbook: [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)

### Tests

```bash
cd backend
set LLM_MODE=mock
pytest -q
```

## Demo paths

1. Urdu food request → Food ticket + resource match + SOP citations  
2. Duplicate phone `03001234567` → HITL pending  
3. Critical medical → Supervisor approve → ticket  
4. Case timeline + PDF export  

See [docs/DEMO_SCRIPT.md](docs/DEMO_SCRIPT.md).

## Docs

| Doc | Purpose |
|-----|---------|
| [docs/PRODUCT_DEFINITION.md](docs/PRODUCT_DEFINITION.md) | Product + Tier A/B/C |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | System design |
| [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) | **Live deploy contract** (ECS Compose) |
| [docs/DEMO_SCRIPT.md](docs/DEMO_SCRIPT.md) | 3-minute demo |
| [AGENTS.md](AGENTS.md) | Product agents |

## Alibaba Cloud

- **DashScope / Qwen** — set `DASHSCOPE_API_KEY` and `LLM_MODE=qwen`
- **Qoder** — official hackathon IDE (Skills / MCP narrative)
- **ECS** — primary live host (`docker compose`); see DEPLOYMENT.md

## Repo

https://github.com/Atif1299/alkhidmat-relief-copilot
