# Demo Script — Alkhidmat Relief Copilot (3 minutes)

## Setup

1. Backend: `cd backend && .venv\Scripts\activate && set LLM_MODE=mock && uvicorn app.main:app --reload --port 8000`
2. Frontend: `cd frontend && npm run dev`
3. Open http://localhost:3000/chat

## Script

### 1. Problem (20s)

Aid requests hit NGOs as messy Urdu/English messages — wrong routing, duplicates, missed critical medical cases.

### 2. Live happy path (90s)

Open **Chat**. Click chip **Urdu · Food** (or paste):

> Flood ke baad khane ki zaroorat hai, Township Lahore, family of 5. Phone 03017654321

Click **Run desk pipeline**. Point to **Agent trace**:
Intake → Triage → Integrity → Matcher → Dispatch → ticket ID.

### 3. Integrity (30s)

Run **EN · Duplicate** chip (phone `03001234567`). Show status `pending_hitl` and duplicate flag. Open **Supervisor**.

### 4. Critical + HITL (30s)

From Chat, run **Critical · Medical**. Go to **Supervisor**, **Approve**. Show ticket created. Open **Dashboard** — cases, time-to-ticket, escalation %.

### 5. Close (20s)

Stack: LangGraph multi-agent + Qwen/DashScope + FastAPI + Next.js — built for Alkhidmat-scale ops with human approval for high risk.
