---
name: alkhidmat-build
description: >-
  Implements Alkhidmat Relief Copilot Tier A then Tier B. LangGraph orchestrator,
  FastAPI, Next.js 14, Qwen/DashScope, HITL supervisor, agent trace UI. Repo:
  github.com/Atif1299/alkhidmat-relief-copilot. Use when user says "start build",
  names a plan todo, or asks to implement agents, API, or UI.
---

# Alkhidmat Relief Copilot — Build Skill

## Before coding

1. Read `docs/PRODUCT_DEFINITION.md` — Tier A/B/C
2. Read `AGENTS.md` — agent contracts
3. **Tier A must be complete and tested before any Tier B work**

## Repository

```
https://github.com/Atif1299/alkhidmat-relief-copilot.git
```

Push `.cursor/` with the codebase. After each todo below: **commit + push**.

## Monorepo layout

```
alkhidmat-relief-copilot/
├── backend/app/          # FastAPI + LangGraph + tools
├── frontend/app/         # Next.js 14 routes
├── docs/
└── .cursor/              # committed
```

## Stack

| Layer | Choice |
|-------|--------|
| Orchestrator | LangGraph — NOT Hermes |
| LLM | DashScope Qwen (`DASHSCOPE_API_KEY`); `LLM_MODE=mock` for offline |
| API | FastAPI |
| DB | SQLAlchemy + SQLite |
| UI | Next.js 14 App Router |

## LangGraph graph (Tier A)

```
Intake → Triage → Integrity → Matcher → Dispatch
              ↓ (critical OR high risk)
         HITL interrupt → Supervisor approve/reject → resume or reject
```

**CaseState fields:** `raw_message`, `language`, `extracted`, `category`, `priority`, `integrity`, `matched_resources`, `ticket_id`, `status`, `agent_trace`, `requires_hitl`, `hitl_decision`

**HITL:** `interrupt_before` dispatch when `requires_hitl=True`. Resume via supervisor API.

## Tier A checklist (ship all before Tier B)

- [ ] A1 Citizen chat Urdu + EN with streaming trace
- [ ] A2 Six-agent pipeline; Integrity never skipped
- [ ] A3 HITL supervisor approve/reject
- [ ] A4 Duplicate phone flagged (seed `03001234567`)
- [ ] A5 Resource matching from Lahore seed
- [ ] A6 Ticket lifecycle statuses
- [ ] A7 Dashboard: cases today, avg time-to-ticket, % escalated
- [ ] A8 Audit log on agent steps + supervisor decisions
- [ ] A9 Qwen integration
- [ ] A10 Three demo scenarios pass E2E tests

## Tier B (after Tier A green)

From `docs/PRODUCT_DEFINITION.md`:

8. Light RAG / SOP Knowledge agent (show retrieval in UI)
9. Role-based views (Requester / Desk / Supervisor)
10. Case timeline (Requested → Matched → Dispatched → Closed)
11. Richer Lahore district seed data
12. Export case PDF/report

## Implementation todos (commit + push each)

1. `chore: initialize monorepo` — structure, README, .env.example
2. `feat(backend): FastAPI skeleton, DB models, seed`
3. `feat(backend): MCP-style tools + audit logger`
4. `feat(agents): LangGraph pipeline mock LLM`
5. `feat(agents): HITL gate + supervisor API`
6. `feat(llm): DashScope Qwen + bilingual prompts`
7. `feat(api): chat endpoint SSE agent trace`
8. `feat(frontend): Next.js 14 shell`
9. `feat(frontend): chat + AgentTrace UI`
10. `feat(frontend): supervisor + tickets views`
11. `feat(dashboard): metrics API + page`
12. `test: E2E happy/duplicate/escalation`
13. `docs: architecture + deploy guide`

## Tools (backend/app/tools/)

| Tool | Used by |
|------|---------|
| `search_similar_cases` | Integrity |
| `list_resources` | Matcher |
| `create_case` | Dispatch |
| `assign_volunteer` | Dispatch |
| `escalate_to_human` | Integrity |
| `send_status_message` | Dispatch |

## API (Tier A)

| Endpoint | Purpose |
|----------|---------|
| POST `/api/v1/chat` | Submit message; SSE agent trace |
| GET `/api/v1/cases` | Ticket list |
| GET `/api/v1/cases/{id}` | Detail + trace |
| GET `/api/v1/supervisor/queue` | Pending HITL |
| POST `/api/v1/supervisor/{id}/decide` | approve/reject |
| GET `/api/v1/metrics` | Dashboard stats |

## Frontend routes (Tier A)

| Route | Purpose |
|-------|---------|
| `/chat` | Citizen demo + AgentTrace sidebar |
| `/tickets` | Ops desk ticket list |
| `/supervisor` | HITL queue |
| `/dashboard` | Metrics for judges |

## Demo scenarios (must pass)

1. Urdu food: `"Flood ke baad khane ki zaroorat hai, Township Lahore, family of 5"`
2. Duplicate: same phone `03001234567` → flagged
3. Critical: `"Chest pain, need ambulance, Johar Town"` → HITL → approve → ticket

## Alibaba Cloud

- DashScope Qwen for all agent LLM calls
- Document ECS/FC deploy in README
- Qoder: dev environment when access arrives

## Do not (Tier A)

- Hermes Agent as orchestrator
- Skip Integrity node
- Skip HITL or Urdu path
- Tier B features before Tier A tests pass
- Real Alkhidmat API
- WhatsApp production
