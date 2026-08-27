---
name: Tier 1 Core Aid Desk
overview: "Tier A / Tier 1 — ship the governed multi-agent aid desk: LangGraph pipeline, HITL supervisor, agent trace UI, duplicate+critical demos, metrics, Qwen/DashScope, audit log. SQLite acceptable for this tier."
todos:
  - id: scaffold
    content: FastAPI + Next.js 14 + LangGraph scaffold; seed Lahore basics
    status: completed
  - id: agents-graph
    content: "Graph Intake → Triage → Integrity → Matcher → Dispatch; never skip Integrity"
    status: completed
  - id: hitl
    content: HITL interrupt + supervisor approve/reject API + UI queue
    status: completed
  - id: chat-trace
    content: Chat SSE + visible agent trace in UI
    status: completed
  - id: demos
    content: Happy path + duplicate phone + critical medical E2E
    status: completed
  - id: metrics-audit
    content: Metrics dashboard + audit log
    status: completed
  - id: qwen
    content: DashScope Qwen wired (LLM_MODE=qwen); mock for offline tests
    status: completed
isProject: false
---

# Tier 1 — Core Aid Desk (Tier A)

**Also called:** Tier A in `docs/PRODUCT_DEFINITION.md`  
**Status:** Complete (E2E green before Tier 2)

## Product goal

Turn Urdu/English aid requests into **verified, resource-matched tickets** with **HITL** for critical / high-risk cases.

**Winning signal:** Desk and requester know what happens next (ticket ID, match, or waiting for supervisor).

## Graph (locked)

```
Intake → Triage → Integrity → Matcher → Dispatch
              ↓ (critical OR high integrity risk)
         HITL interrupt → Supervisor approve/reject
```

Knowledge (RAG) is **not** in Tier 1 — added in Tier 2.

## Acceptance (A1–A10)

| # | Feature | Done when |
|---|---------|-----------|
| 1 | Agent trace visible in UI | Chat shows each agent step |
| 2 | HITL supervisor | Approve/reject pending cases |
| 3 | Duplicate + critical demos | Phone `03001234567`; critical medical → HITL |
| 4 | Metrics dashboard | Cases, time-to-ticket, escalation % |
| 5 | Urdu + English | Both paths work live |
| 6 | Qwen / DashScope | Real LLM when key set |
| 7 | Audit log | Approvals / decisions recorded |
| 8–10 | Ticket lifecycle | Create, list, detail |

## Stack (this tier)

| Layer | Choice |
|-------|--------|
| Orchestration | LangGraph |
| LLM | DashScope Qwen (`LLM_MODE=mock\|qwen`) |
| API | FastAPI |
| DB | SQLite (Postgres later in Tier 3) |
| UI | Next.js 14 App Router |

## Out of scope

Role switcher / Knowledge RAG / PDF / rich seed → **Tier 2**  
JWT / Postgres / pgvector → **Tier 3**  
WhatsApp / Alkhidmat ERP / marketplace → **Tier C**

## Teammate notes

- Repo: https://github.com/Atif1299/alkhidmat-relief-copilot  
- Source of truth: `docs/PRODUCT_DEFINITION.md`  
- Do not skip Integrity on create.
