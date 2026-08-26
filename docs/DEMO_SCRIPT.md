# Demo Script — Alkhidmat Relief Copilot (3 minutes + Tier B)

## Setup

1. Backend: `cd backend && .venv\Scripts\activate && set LLM_MODE=mock && uvicorn app.main:app --reload --port 8000`
2. Frontend: `cd frontend && npm run dev`
3. Open http://localhost:3000/chat
4. Role switcher (top right): start as **Desk** or **Supervisor**

## Script

### 1. Problem (20s)

Aid requests hit NGOs as messy Urdu/English messages — wrong routing, duplicates, missed critical medical cases.

### 2. Live happy path (70s)

Open **Chat**. Click chip **Urdu · Food** (or paste):

> Flood ke baad khane ki zaroorat hai, Township Lahore, family of 5. Phone 03017654321

Click **Run desk pipeline**. Point to **Agent trace**:
Intake → Triage → **Knowledge** → Integrity → Matcher → Dispatch → ticket ID.

Show **Sources / SOPs used** citations under the result.

### 3. Integrity (25s)

Run **EN · Duplicate** chip (phone `03001234567`). Show status `pending_hitl` and duplicate flag. Open **Supervisor**.

### 4. Critical + HITL (25s)

From Chat, run **Critical · Medical**. Go to **Supervisor**, **Approve**. Show ticket created. Open **Dashboard** — cases, time-to-ticket, escalation %.

### 5. Tier B ops beat (30s)

1. Open the case from **Tickets** (or `/cases/{id}`).
2. Show **status timeline** (requested → … → dispatched) and SOP citations.
3. Click **Export PDF** — ticket summary for desk/supervisor.
4. Flip role switcher to **Requester** — nav hides Tickets/Supervisor/Dashboard (chat only). Flip to **Supervisor** — full ops views.

Narrative: *Governed agents + Alkhidmat SOPs + ops-ready export — not a chatbot.*

### 6. Close (15s)

Stack: LangGraph multi-agent + Qwen/DashScope + FastAPI + Next.js — Alkhidmat-scale ops with human approval for high risk.
