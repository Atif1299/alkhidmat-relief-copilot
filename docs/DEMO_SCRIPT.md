# Demo Script — Alkhidmat Relief Copilot (3 minutes)

## Setup

1. Postgres: `docker compose up -d db` (or full stack `docker compose up`)
2. Backend: `cd backend && .venv\Scripts\activate && set LLM_MODE=mock && uvicorn app.main:app --reload --port 8000`
3. Frontend: `cd frontend && npm run dev`
4. Open http://localhost:3000 — **landing** (not login)

| Email | Role | Use |
|-------|------|-----|
| desk@aiddesk.example | Desk | Tickets, dashboard, PDF |
| supervisor@aiddesk.example | Supervisor | Full ops + HITL |
| Password (both) | | `AidDesk!2026` |

Citizens do **not** log in — they use **Request aid**.

## Script

### 1. Problem (15s)

Aid requests hit NGOs as messy Urdu/English messages — wrong routing, duplicates, missed critical medical cases.

### 2. Landing + citizen path (70s)

Open **/**. Point to dual CTAs: **Request aid** vs **Staff sign in**.

Click **Request aid**. Show live **pipeline strip**. Click chip **Urdu · Food** (or paste):

> Flood ke baad khane ki zaroorat hai, Township Lahore, family of 5. Phone 03017654321

Click **Submit request**. Point to **Agent trace**:
Intake → Triage → **Knowledge** → Integrity → Matcher → Dispatch → **ticket ID** above the fold.

Show **SOP citations**. No login required.

### 3. Integrity / HITL (40s)

Still on Request aid (or staff Test intake), run **EN · Duplicate** or **Critical · Medical**. Show status **Waiting for supervisor**.

**Staff sign in** as `supervisor@aiddesk.example`. Land on **Tickets**. Open **Supervisor**, **Approve**. Show ticket created. Open **Dashboard** — cases, time-to-ticket, pending HITL.

### 4. Ops beat (30s)

1. Open the case from **Tickets** (or case detail).
2. Show **status timeline** and SOP citations.
3. Click **Export PDF**.
4. Optional: logout → landing → prove citizen path still works without staff nav.

Narrative: *Citizen submits without an account → desk sees a verified ticket → supervisor only when needed.*

### 5. Close (15s)

Stack: LangGraph multi-agent + Qwen/DashScope + FastAPI + Postgres/pgvector + Next.js — Alkhidmat-scale ops with human approval for high risk.
