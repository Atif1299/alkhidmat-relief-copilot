---
name: alkhidmat-build
description: >-
  Implements Alkhidmat Relief Copilot Tier A then Tier B. LangGraph orchestrator,
  FastAPI, Next.js 14, Qwen/DashScope, HITL supervisor, agent trace UI, Knowledge
  RAG, roles, timeline, PDF. Repo: github.com/Atif1299/alkhidmat-relief-copilot.
  Use when user says "start build", names a plan todo, or asks to implement agents,
  API, or UI.
---

# Alkhidmat Relief Copilot — Build Skill

## Before coding

1. Read `docs/PRODUCT_DEFINITION.md` — Tier A/B/C
2. Read `docs/ARCHITECTURE.md` — current graph
3. Read `AGENTS.md` — agent contracts
4. **Tier A must be complete and tested before any Tier B work** (Tier A is green)

## Repository

```
https://github.com/Atif1299/alkhidmat-relief-copilot.git
```

Push `.cursor/` with the codebase. After each todo: **commit + push**.

## Stack

| Layer | Choice |
|-------|--------|
| Orchestrator | LangGraph — NOT Hermes |
| LLM | DashScope Qwen; `LLM_MODE=mock` for offline |
| Knowledge | SOP markdown → `sop_chunks` + keyword search |
| API | FastAPI |
| DB | SQLAlchemy + SQLite |
| UI | Next.js 14 App Router |
| PDF | reportlab |

## LangGraph graph (Tier B)

```
Intake → Triage → Knowledge → Integrity → Matcher → Dispatch
                         ↓ (critical OR high risk)
                    HITL interrupt → Supervisor approve/reject → resume or reject
```

**CaseState:** Tier A fields + `sop_hits` (list of title/category/excerpt/score).

**Non-negotiable:** Integrity never skipped. Knowledge after Triage, before Integrity.

## Tier A checklist (complete)

- [x] A1–A10 (chat, pipeline, HITL, duplicate, matcher, lifecycle, dashboard, audit, Qwen, E2E)

## Tier B checklist

- [ ] B8 Knowledge step + SOP citations in UI
- [ ] B9 Role switcher: requester | desk | supervisor (localStorage)
- [ ] B10 Case timeline API + `/cases/[id]` page
- [ ] B11 ≥25 Lahore resources + SOP corpus
- [ ] B12 PDF export endpoint + UI button
- [ ] Tier A E2E still pass

## Tier B implementation todos (commit + push each)

1. `docs: lock Tier B architecture and Cursor build guidance`
2. `feat(seed): expand Lahore inventory and SOP corpus`
3. `feat(agents): add Knowledge RAG node with SOP retrieval`
4. `feat(api): add case timeline endpoint`
5. `feat(api): add PDF case export`
6. `feat(frontend): role views, case timeline, SOP citations, PDF export`
7. `test: Tier B knowledge, timeline, and PDF coverage`

## Tools

| Tool | Used by |
|------|---------|
| `search_similar_cases` | Integrity |
| `search_sops` | Knowledge |
| `list_resources` | Matcher |
| `create_case` | Dispatch |
| `assign_volunteer` | Dispatch |
| `escalate_to_human` | Integrity |
| `send_status_message` | Dispatch |

## API

| Endpoint | Purpose |
|----------|---------|
| POST `/api/v1/chat` | SSE agent trace (+ Knowledge) |
| GET `/api/v1/cases` | Ticket list |
| GET `/api/v1/cases/{id}` | Detail + events + sop_hits |
| GET `/api/v1/cases/{id}/timeline` | Product timeline stages |
| GET `/api/v1/cases/{id}/export.pdf` | PDF report |
| GET `/api/v1/supervisor/queue` | Pending HITL |
| POST `/api/v1/supervisor/{id}/decide` | approve/reject |
| GET `/api/v1/metrics` | Dashboard stats |

## Frontend routes

| Route | Roles |
|-------|-------|
| `/chat` | requester, desk, supervisor |
| `/tickets` | desk, supervisor |
| `/cases/[id]` | desk, supervisor |
| `/supervisor` | supervisor |
| `/dashboard` | desk, supervisor |

## Demo scenarios

1. Urdu food → Knowledge SOP citation → Food ticket
2. Duplicate phone `03001234567` → HITL
3. Critical medical → HITL → approve → ticket
4. Open case detail → timeline + Export PDF
5. Flip role switcher (Requester hides Supervisor)

## Do not

- Hermes as orchestrator
- Skip Integrity or Knowledge on create path
- JWT/OAuth (use demo role switcher)
- Vector DB / Tier C features
- Break Tier A E2E paths
