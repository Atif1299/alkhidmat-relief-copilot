# System Overview — Alkhidmat Relief Copilot

**Purpose of this document:** A complete guide to what the project is, how it works, and how every major piece fits together. Use this for onboarding, demos, and judge Q&A.

**Last updated:** 2026-08-30  
**Related docs:** [PRODUCT_DEFINITION.md](PRODUCT_DEFINITION.md) · [ARCHITECTURE.md](ARCHITECTURE.md) · [DEMO_SCRIPT.md](DEMO_SCRIPT.md)

---

## 1. What is this project?

**Alkhidmat Relief Copilot** is an **NGO aid desk SaaS** built for the **Alibaba Cloud AI Hackathon Pakistan 2026**. It is **not** a chatbot — it is an **agentic operations desk** that turns messy Urdu/English aid requests into **verified, prioritized, resource-matched tickets**, with a **human supervisor gate** for high-risk cases.

### One-line pitch

> A multi-agent AI desk that turns an aid request (Urdu/English) into a verified, routed relief ticket — with human approval for high-risk cases.

### What makes it different from a chatbot

| Chatbot | Alkhidmat Relief Copilot |
|---------|--------------------------|
| Replies in natural language | Runs a **fixed agent pipeline** with tools |
| No audit trail | Full **agent trace** + case timeline |
| No fraud checks | **Integrity** agent catches duplicates |
| No resource matching | **Matcher** finds inventory + volunteers |
| No human gate | **Supervisor HITL** for critical/risky cases |
| No ticket ID | Creates **AKD-YYYYMMDD-XXXXXX** tickets |

### Winning signal (what judges look for)

Both the **citizen** and the **desk operator** know **what happens next**:
- Ticket ID created
- Resource matched
- Or: "Waiting for supervisor approval"

---

## 2. Problem it solves

NGO relief desks (like Alkhidmat Lahore) receive aid requests as:
- Messy free text in **Urdu or English**
- Incomplete contact/location info
- Wrong category (food vs medical)
- **Duplicate** requests from same phone
- **Critical** medical cases buried in the queue

**The first 60 seconds** after a request arrives are the bottleneck: classify → verify → match → open ticket (or escalate).

**Promise:** From free-text request → verified ticket + next action in under a minute.

---

## 3. Who uses it?

| Role | Who | What they do | UI entry |
|------|-----|--------------|----------|
| **Citizen / Requester** | Public | Submits aid need; checks status later (no account) | `/request`, `/status` |
| **Desk operator** | NGO staff | Views tickets, traces, metrics | `/login` → `/tickets` |
| **Supervisor** | Senior staff | Approves/rejects high-risk cases | `/login` → `/supervisor` |

### Demo login (password: `AidDesk!2026`)

| Email | Role |
|-------|------|
| `desk@aiddesk.example` | desk |
| `supervisor@aiddesk.example` | supervisor |
| `citizen@aiddesk.example` | requester (API tests only; citizens use `/request` and `/status` without login) |

---

## 4. Tech stack

| Layer | Technology | Why |
|-------|------------|-----|
| **Orchestration** | LangGraph | Multi-agent pipeline with HITL interrupt + durable checkpoints |
| **LLM** | Qwen via DashScope | Alibaba Cloud hackathon requirement |
| **Embeddings** | DashScope `text-embedding-v2` | Vector RAG for SOP retrieval |
| **API** | FastAPI + SSE | REST + streaming agent steps |
| **Database** | PostgreSQL + pgvector | Cases, users, vectors, LangGraph checkpoints |
| **Frontend** | Next.js 14 (App Router) | Public landing + staff ops UI |
| **Auth** | JWT (HS256) + bcrypt | Role-based API gates |
| **PDF export** | reportlab | Case summary for ops |
| **Deploy** | Docker Compose (local) / GCP Cloud Run (live) | |

### What we deliberately did NOT use

- **Hermes gateway** — product needs deterministic NGO workflow + custom UI
- **SQLite in production** — retired; Postgres is the target (tests may still use SQLite)
- **OpenAI-only stack** — hackathon requires Alibaba Cloud Qwen

---

## 5. High-level architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         FRONTEND (Next.js 14)                           │
│  / landing  │  /request  │  /status  │  /login  │  /tickets  │  /supervisor │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │ HTTP / SSE
┌──────────────────────────────▼──────────────────────────────────────────┐
│                         BACKEND (FastAPI)                               │
│  /chat  │  /public/status  │  /cases  │  /supervisor  │  /metrics  │  /auth |
└──────────────────────────────┬──────────────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────────────┐
│                    LANGGRAPH AGENT PIPELINE                              │
│  Intake → Triage → Knowledge → Integrity → [HITL?] → Matcher → Dispatch│
└──────────────────────────────┬──────────────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────────────┐
│              POSTGRESQL + pgvector                                       │
│  cases │ case_events │ resources │ volunteers │ sop_chunks │ users       │
│  LangGraph checkpoints (Linux/Docker)                                    │
└─────────────────────────────────────────────────────────────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │  DashScope (Qwen)   │
                    │  LLM + Embeddings   │
                    └─────────────────────┘
```

---

## 6. The agent pipeline (core of the product)

Every aid request runs through this **LangGraph** pipeline. **Integrity is never skipped** on create — this is a non-negotiable product rule.

```
START
  │
  ▼
┌─────────┐
│ INTAKE  │  Detect language, extract need/location/phone/name
└────┬────┘
     ▼
┌─────────┐
│ TRIAGE  │  Classify: Food, Medical, Shelter, Blood, Education, Other
└────┬────┘       + priority: low / medium / high / critical
     ▼
┌───────────┐
│ KNOWLEDGE │  Retrieve Alkhidmat SOPs (vector RAG or keyword fallback)
└────┬──────┘
     ▼
┌───────────┐
│ INTEGRITY │  Duplicate phone check, risk score, fraud heuristics
└────┬──────┘
     │
     ├── requires HITL? ──YES──► ┌───────────┐
     │                           │ HITL GATE │  Pause graph; wait for supervisor
     │                           └─────┬─────┘
     │                                 │ approve → continue
     │                                 │ reject  → END (case rejected)
     NO                                │
     │◄────────────────────────────────┘
     ▼
┌─────────┐
│ MATCHER │  Match inventory + assign volunteer by category/area
└────┬────┘
     ▼
┌──────────┐
│ DISPATCH │  Create ticket AKD-YYYYMMDD-XXXXXX, notify requester
└────┬─────┘
     ▼
    END
```

### Agent details

| Agent | File | What it does | Tools / services |
|-------|------|--------------|------------------|
| **Intake** | `nodes.py` → `intake_node` | Language detect + structured extraction | `llm.extract_with_llm()` |
| **Triage** | `triage_node` | Category + priority classification | `llm.classify_with_llm()` |
| **Knowledge** | `knowledge_node` | SOP retrieval for category/rules | `sops.search_sops()` |
| **Integrity** | `integrity_node` | Duplicate phone, risk score, HITL flag | `cases.search_similar_cases()` |
| **Supervisor (HITL)** | `hitl_gate_node` | Pause/resume; approve or reject | LangGraph checkpoint + `resume_after_hitl()` |
| **Matcher** | `matcher_node` | Find resources + volunteer | `cases.list_resources()`, `assign_volunteer()` |
| **Dispatch** | `dispatch_node` | Create ticket, log audit, notify | `cases.create_case()`, `send_status_message()` |

### HITL triggers (Human-In-The-Loop)

The graph pauses at `hitl_gate` when **any** of these is true:
- **Duplicate phone** in last 48 hours
- **Critical priority** (e.g. chest pain, ambulance)
- **Risk score ≥ 0.75**
- **Missing phone number** (elevated risk)

Supervisor approves → graph resumes → Matcher → Dispatch → ticket created.  
Supervisor rejects → case status = `rejected` → graph ends.

### Agent trace

Every step appends to `agent_trace` — a JSON array of `{agent, action, detail, ts_ms}` objects. The UI streams these via **Server-Sent Events (SSE)** so operators see the pipeline live.

---

## 7. Request flow (end to end)

### A. Citizen submits aid request (public)

1. User opens **`/request`** (no login)
2. Types or picks a sample message (Urdu food, duplicate phone, critical medical)
3. Frontend calls **`POST /api/v1/chat`** with SSE
4. Backend runs LangGraph pipeline
5. UI shows:
   - **Pipeline strip** (which agents ran)
   - **Agent trace** (step-by-step log)
   - **SOP citations** (what Knowledge retrieved)
   - **Result**: AKD request number (minted at intake, including HITL), or wait-for-supervisor
6. Later, citizen opens **`/status`** with that number plus the same phone (no account)

### B. Supervisor approves HITL case

1. Supervisor logs in → **`/supervisor`**
2. Sees queue of `pending_hitl` cases
3. Clicks Approve or Reject with optional note
4. API: **`POST /api/v1/supervisor/{case_id}/decide`**
5. Backend calls **`resume_after_hitl()`** — LangGraph continues from checkpoint
6. If approved: Matcher + Dispatch run → ticket created

### C. Desk operator reviews cases

1. Desk logs in → **`/tickets`** (default home)
2. Lists all cases with status, category, priority
3. Opens case detail → **`/cases/[id]`**
4. Sees timeline, agent trace, SOP hits, PDF export

---

## 8. Backend structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app, lifespan, routers
│   ├── config.py            # Settings from .env (LLM, DB, JWT, CORS)
│   ├── schemas.py           # Pydantic request/response models
│   │
│   ├── agents/
│   │   ├── graph.py         # LangGraph compile, run_pipeline, resume_after_hitl
│   │   ├── nodes.py         # All agent node functions
│   │   ├── state.py         # CaseState TypedDict (shared graph state)
│   │   └── prompts/         # Qwen system prompts for Intake/Triage
│   │
│   ├── api/
│   │   ├── auth.py          # POST /login, GET /me
│   │   ├── chat.py          # POST /chat (SSE), /chat/sync
│   │   ├── cases.py         # List, detail, timeline, PDF export
│   │   ├── supervisor.py    # HITL queue + decide
│   │   └── metrics.py       # Dashboard stats
│   │
│   ├── db/
│   │   ├── models.py        # SQLAlchemy: Case, Resource, Volunteer, SopChunk, User
│   │   ├── session.py       # DB engine, init_db (pgvector extension)
│   │   └── seed.py          # Lahore demo data (resources, volunteers, users)
│   │
│   ├── deps/
│   │   └── auth.py          # JWT validation, RequireDesk, RequireSupervisor
│   │
│   ├── services/
│   │   ├── llm.py           # mock vs Qwen extract/classify
│   │   ├── embeddings.py    # DashScope embedding calls
│   │   ├── audit.py         # CaseEvent logging
│   │   ├── timeline.py      # Build case lifecycle stages
│   │   ├── pdf_export.py    # reportlab case PDF
│   │   └── security.py      # bcrypt + JWT create/verify
│   │
│   ├── tools/               # MCP-style functions agents call
│   │   ├── cases.py         # search_similar, list_resources, create_case, etc.
│   │   ├── sops.py          # index + search SOPs (vector + keyword)
│   │   └── reindex_sops.py  # CLI to re-embed SOPs
│   │
│   └── knowledge/sops/      # Markdown SOP files
│       ├── food.md, medical.md, shelter.md, blood.md, education.md
│       ├── integrity_hitl.md, urdu_faq.md
│
├── tests/                   # pytest (mock LLM mode)
├── requirements.txt
└── Dockerfile
```

---

## 9. Frontend structure

```
frontend/
├── app/
│   ├── page.tsx             # Public landing (Request aid + Staff sign in)
│   ├── request/page.tsx     # Guest intake with SSE agent trace
│   ├── login/page.tsx       # Staff JWT login
│   ├── tickets/page.tsx     # Case list (desk home)
│   ├── cases/[id]/page.tsx  # Case detail + timeline + PDF
│   ├── supervisor/page.tsx  # HITL approve/reject queue
│   ├── dashboard/page.tsx   # Metrics (cases today, avg time, escalations)
│   ├── chat/page.tsx        # Staff test sandbox
│   └── layout.tsx           # App shell
│
├── components/
│   ├── AgentTrace.tsx       # Step-by-step agent log
│   ├── PipelineStrip.tsx    # Visual pipeline progress
│   ├── SopCitations.tsx     # Retrieved SOP excerpts
│   ├── CaseTimeline.tsx     # Requested → Matched → Dispatched stages
│   └── AppChrome.tsx        # Nav, auth-aware header
│
└── lib/
    ├── api.ts               # All API calls + SSE chatStream
    ├── auth.ts              # JWT token in localStorage
    └── roles.ts             # Role-based nav gating
```

### Route map

| Route | Auth | Purpose |
|-------|------|---------|
| `/` | Public | Landing page |
| `/request` | **None** (guest chat) | Citizen aid intake |
| `/status` | **None** (guest) | Look up request with AKD number + phone |
| `/login` | Public | Staff sign-in |
| `/tickets` | JWT (desk+) | Case management |
| `/cases/[id]` | JWT (requester+) | Case detail |
| `/supervisor` | JWT (supervisor) | HITL queue |
| `/dashboard` | JWT (desk+) | Ops metrics |
| `/chat` | JWT | Staff test intake |

---

## 10. Database schema

### Core tables

| Table | Purpose |
|-------|---------|
| **cases** | Every aid request: message, category, status, ticket_id, agent_trace, risk |
| **case_events** | Audit log: who did what, when (Integrity, Supervisor, Matcher, etc.) |
| **resources** | Lahore inventory: food kitchens, clinics, shelters, blood banks |
| **volunteers** | Field volunteers with skills + area |
| **sop_chunks** | Indexed SOP markdown + embeddings (JSON + pgvector column) |
| **users** | Staff accounts with roles |

### Case statuses

| Status | Meaning |
|--------|---------|
| `processing` | Pipeline running |
| `pending_hitl` | Paused — waiting for supervisor |
| `dispatched` | Ticket created, resource matched |
| `rejected` | Supervisor rejected |
| `open` / `closed` / `flagged_duplicate` | Extended lifecycle |

### Ticket ID format

`AKD-YYYYMMDD-XXXXXX` (e.g. `AKD-20260830-A1B2C3`) — minted at intake, not only at Dispatch.

---

## 11. API reference (summary)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/health` | None | Service health + tier info |
| POST | `/api/v1/auth/login` | None | Returns JWT |
| GET | `/api/v1/auth/me` | JWT | Current user |
| POST | `/api/v1/chat` | Optional | SSE agent pipeline |
| POST | `/api/v1/chat/sync` | Optional | Sync pipeline (tests) |
| POST | `/api/v1/public/status` | None | Citizen lookup: ticket + phone; 404 on mismatch |
| GET | `/api/v1/cases` | desk | List cases |
| GET | `/api/v1/cases/{id}` | requester+ | Case + timeline |
| GET | `/api/v1/cases/{id}/timeline` | desk | Lifecycle stages |
| GET | `/api/v1/cases/{id}/export.pdf` | desk | PDF download |
| GET | `/api/v1/supervisor/queue` | supervisor | HITL pending cases |
| POST | `/api/v1/supervisor/{id}/decide` | supervisor | approve / reject |
| GET | `/api/v1/metrics` | desk | Dashboard stats |

**Guest chat:** `/request` works without login — `OptionalChatUser` allows anonymous `POST /chat`.  
**Guest status:** `/status` calls `POST /api/v1/public/status` with no JWT. Wrong ticket or phone returns the same 404 (`Request not found`). Payload is citizen-only (no trace, risk, HITL notes, volunteer phone).

---

## 12. Knowledge / RAG (Tier B)

SOPs live as markdown in `backend/app/knowledge/sops/`. On startup, `seed.py` indexes them into `sop_chunks`.

**Retrieval order:**
1. **pgvector cosine** (Postgres + DashScope embeddings) — preferred
2. **Python cosine** on JSON embeddings — fallback
3. **Keyword scoring** — always available without API key

The Knowledge agent retrieves top 3 SOPs for the case category + query. Results appear in:
- Agent trace (`retrieval_mode: vector | keyword`)
- UI `SopCitations` component
- Case record `sop_hits` JSON field

Matcher uses SOP text to **boost** resource names mentioned in retrieved excerpts.

---

## 13. LLM modes

| `LLM_MODE` | Behavior |
|------------|----------|
| `mock` | Keyword heuristics — no API key needed (tests, offline dev) |
| `qwen` | Real DashScope Qwen calls for Intake + Triage |

Set in `.env`:
```
LLM_MODE=mock
DASHSCOPE_API_KEY=sk-...
DASHSCOPE_MODEL=qwen-plus
```

Mock mode still detects Urdu script, Lahore areas, phone `03XXXXXXXXX`, critical keywords.

---

## 14. Authentication & roles

- **JWT** stored in browser `localStorage` after login
- **bcrypt** password hashes in `users` table
- API dependencies: `RequireDesk`, `RequireSupervisor`, `RequireRequester`
- `AUTH_DISABLED=true` — emergency dev mode (all gates open)

Role capabilities:
- **requester** — view own case detail
- **desk** — list cases, metrics, timeline, PDF
- **supervisor** — all desk + HITL queue/decide

---

## 15. Demo scenarios (built-in)

Three sample messages on `/request`:

| Sample | What happens |
|--------|--------------|
| **Urdu · Food** | Food category → Township kitchen matched → ticket |
| **EN · Duplicate** | Phone `03001234567` (seeded duplicate) → HITL pending |
| **Critical · Medical** | Critical priority → HITL pending → supervisor approves → ambulance/clinic |

See [DEMO_SCRIPT.md](DEMO_SCRIPT.md) for the 3-minute pitch flow.

---

## 16. Environment variables

| Variable | Purpose |
|----------|---------|
| `DATABASE_URL` | Postgres connection string |
| `LLM_MODE` | `mock` or `qwen` |
| `DASHSCOPE_API_KEY` | Alibaba Cloud API key |
| `DASHSCOPE_MODEL` | e.g. `qwen-plus` |
| `DASHSCOPE_EMBEDDING_MODEL` | e.g. `text-embedding-v2` |
| `JWT_SECRET` | HS256 signing secret (32+ chars in prod) |
| `AUTH_DISABLED` | `true` to bypass auth (dev only) |
| `CORS_ORIGINS` | Frontend origin(s) |
| `NEXT_PUBLIC_API_URL` | Frontend → API base URL |

Copy from `.env.example` at repo root.

---

## 17. How to run locally

### Option A: Docker Compose (recommended)

```bash
docker compose up -d
# API: http://localhost:8000
# Web: http://localhost:3000
```

### Option B: Manual

```bash
# 1. Start Postgres
docker compose up -d db

# 2. Backend
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
copy ..\.env.example .env
set LLM_MODE=mock
uvicorn app.main:app --reload --port 8000

# 3. Frontend
cd frontend
npm install
copy .env.local.example .env.local
npm run dev
```

Open **http://localhost:3000** — citizens use **Request aid**; staff use **Staff sign in**.

### Tests

```bash
cd backend
set LLM_MODE=mock
pytest -q
```

---

## 18. Deployment (live)

| Surface | URL |
|---------|-----|
| Web | https://relief-web-4idrhaffca-el.a.run.app |
| API | https://relief-api-4idrhaffca-el.a.run.app |

- **GCP Cloud Run** for API + Web
- **Cloud SQL Postgres + pgvector** for data
- **Secret Manager** for DashScope + JWT secrets
- **DashScope** for LLM + embeddings (Alibaba Cloud)

Details: [DEPLOYMENT.md](DEPLOYMENT.md)

---

## 19. Product tiers (what's built vs deferred)

### Tier A — Must (all implemented)

1. Agent trace in UI  
2. HITL supervisor queue  
3. Duplicate + critical demo paths  
4. Metrics dashboard  
5. Urdu + English live  
6. Qwen/DashScope wired  
7. Audit log  

### Tier B — High value (implemented)

8. Knowledge / light RAG  
9. Role-based views  
10. Case timeline  
11. Lahore seed inventory  
12. PDF export  

### Tier 3 — Production hardening (implemented)

13. Docker Postgres + pgvector  
14. JWT auth + role gates  
15. Vector RAG + keyword fallback  
16. GCP Cloud Run deploy  

### Tier C — Deferred

WhatsApp production, real Alkhidmat API, mobile apps, billing, CNIC OCR.

---

## 20. Key design decisions

| Decision | Why |
|----------|-----|
| LangGraph over Hermes | Deterministic NGO workflow + HITL interrupt |
| Integrity never skipped | Fraud/duplicate protection is core product value |
| Guest `/request` + `/status` | Citizens don't need accounts; they track with AKD number + phone |
| SSE for chat | Operators see agents work in real time |
| Mock LLM mode | Tests and offline dev without API costs |
| Postgres checkpoints (Linux) | Durable HITL pause/resume across restarts |
| SQLite checkpoints (Windows dev) | psycopg async limitation on Windows ProactorEventLoop |

Full log: [DECISIONS.md](DECISIONS.md)

---

## 21. Glossary

| Term | Meaning |
|------|---------|
| **HITL** | Human-In-The-Loop — supervisor must approve before ticket |
| **SOP** | Standard Operating Procedure — NGO rules stored as markdown |
| **Agent trace** | JSON log of every agent step for a case |
| **Case** | Internal UUID record for one aid request |
| **Ticket** | Public receipt (`AKD-...`) minted at intake; Dispatch means verified + matched |
| **DashScope** | Alibaba Cloud API for Qwen LLM + embeddings |
| **pgvector** | Postgres extension for cosine similarity search |

---

## 22. Quick reference — file to feature map

| Feature | Primary files |
|---------|---------------|
| Agent pipeline | `backend/app/agents/graph.py`, `nodes.py` |
| Chat API + SSE | `backend/app/api/chat.py` |
| HITL resume | `backend/app/agents/graph.py` → `resume_after_hitl()` |
| SOP RAG | `backend/app/tools/sops.py`, `knowledge/sops/*.md` |
| Duplicate detection | `backend/app/tools/cases.py` → `search_similar_cases()` |
| Public intake UI | `frontend/app/request/page.tsx` |
| Public status check | `frontend/app/status/`, `backend/app/api/public.py` |
| Supervisor UI | `frontend/app/supervisor/page.tsx` |
| Demo seed data | `backend/app/db/seed.py` |
| PDF export | `backend/app/services/pdf_export.py` |
| Metrics | `backend/app/api/metrics.py`, `frontend/app/dashboard/page.tsx` |

---

*For implementation steps when building new features, see `.cursor/skills/alkhidmat-build/SKILL.md`.*
