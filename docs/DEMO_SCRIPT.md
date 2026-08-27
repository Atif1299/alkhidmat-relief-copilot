# Demo Script — Alkhidmat Relief Copilot (3 minutes + Tier 3 auth)

## Setup

1. Postgres: `docker compose up -d db` (or full stack `docker compose up`)
2. Backend: `cd backend && .venv\Scripts\activate && set LLM_MODE=mock && uvicorn app.main:app --reload --port 8000`
3. Frontend: `cd frontend && npm run dev`
4. Open http://localhost:3000/login — password for all demo users: `AidDesk!2026`

| Email | Role |
|-------|------|
| supervisor@aiddesk.example | Supervisor (full ops + HITL) |
| desk@aiddesk.example | Desk (tickets, dashboard, PDF) |
| citizen@aiddesk.example | Requester (chat only) |

## Script

### 1. Problem (20s)

Aid requests hit NGOs as messy Urdu/English messages — wrong routing, duplicates, missed critical medical cases.

### 2. Login + happy path (70s)

Login as **supervisor@aiddesk.example**. Open **Chat**. Click chip **Urdu · Food** (or paste):

> Flood ke baad khane ki zaroorat hai, Township Lahore, family of 5. Phone 03017654321

Click **Run desk pipeline**. Point to **Agent trace**:
Intake → Triage → **Knowledge** → Integrity → Matcher → Dispatch → ticket ID.

Show **Sources / SOPs used** citations. If DashScope embeddings are configured, Knowledge shows vector retrieval in the trace (`via vector`); otherwise keyword fallback.

### 3. Integrity (25s)

Run **EN · Duplicate** chip (phone `03001234567`). Show status `pending_hitl` and duplicate flag. Open **Supervisor**.

### 4. Critical + HITL (25s)

From Chat, run **Critical · Medical**. Go to **Supervisor**, **Approve**. Show ticket created. Open **Dashboard** — cases, time-to-ticket, escalation %.

### 5. Ops beat + role proof (30s)

1. Open the case from **Tickets** (or `/cases/{id}`).
2. Show **status timeline** and SOP citations.
3. Click **Export PDF**.
4. **Logout** → login as **citizen@aiddesk.example** — nav is chat-only; Tickets/Supervisor/Dashboard hidden. Logout → login as **supervisor** again for full ops.

Narrative: *Governed agents + real JWT roles + Alkhidmat SOPs — not a chatbot.*

### 6. Close (15s)

Stack: LangGraph multi-agent + Qwen/DashScope (+ embeddings) + FastAPI + Postgres/pgvector + Next.js — Alkhidmat-scale ops with human approval for high risk.
