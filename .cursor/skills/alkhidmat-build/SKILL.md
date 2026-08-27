---
name: alkhidmat-build
description: >-
  Implements Alkhidmat Relief Copilot Tier A → B → 3. LangGraph orchestrator,
  FastAPI, Next.js 14, Qwen/DashScope, JWT auth, Postgres/pgvector Knowledge RAG,
  HITL supervisor, agent trace UI, timeline, PDF. Repo:
  github.com/Atif1299/alkhidmat-relief-copilot. Use when user says "start build",
  names a plan todo, or asks to implement agents, API, or UI.
---

# Alkhidmat Relief Copilot — Build Skill

## Before coding

1. Read `docs/PRODUCT_DEFINITION.md` — Tier A / B / 3 / C
2. Read `docs/ARCHITECTURE.md` — current graph
3. Read `AGENTS.md` — agent contracts
4. **Tier A → B green before Tier 3**; do not start Tier C unless rubric demands

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
| Knowledge | SOP markdown → embeddings + **pgvector** / cosine + keyword fallback |
| Auth | JWT (`/auth/login`, `/auth/me`) + API role gates |
| API | FastAPI |
| DB | **Postgres/pgvector** (Compose `db`); SQLite tests only |
| UI | Next.js 14 App Router + `/login` |
| PDF | reportlab |

## LangGraph graph

```
Intake → Triage → Knowledge → Integrity → Matcher → Dispatch
                         ↓ (critical OR high risk)
                    HITL interrupt → Supervisor approve/reject → resume or reject
```

**CaseState:** + `sop_hits` (title/category/excerpt/score/`retrieval_mode`).

**Non-negotiable:** Integrity never skipped. Knowledge after Triage, before Integrity.

## Tier A / B (complete)

- [x] A1–A10 + B8–B12

## Tier 3 — Production Hardening

- [x] Docker Postgres + pgvector
- [x] JWT users + API role gates
- [x] Frontend login + Bearer client
- [x] Vector RAG + keyword fallback (`python -m app.tools.reindex_sops`)
- [ ] GCP promote (JWT secret + vector ext + redeploy) when asked

Demo users (password `AidDesk!2026`):
`citizen@` / `desk@` / `supervisor@aiddesk.example`

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

| Endpoint | Purpose | Roles |
|----------|---------|-------|
| POST `/api/v1/auth/login` | JWT | public |
| GET `/api/v1/auth/me` | Current user | auth |
| POST `/api/v1/chat` | SSE agent trace | requester+ |
| GET `/api/v1/cases` | Ticket list | desk+ |
| GET `/api/v1/cases/{id}` | Detail | requester+ |
| GET `/api/v1/cases/{id}/timeline` | Timeline | desk+ |
| GET `/api/v1/cases/{id}/export.pdf` | PDF | desk+ |
| GET `/api/v1/supervisor/queue` | Pending HITL | supervisor |
| POST `/api/v1/supervisor/{id}/decide` | approve/reject | supervisor |
| GET `/api/v1/metrics` | Dashboard | desk+ |

## Frontend routes

| Route | Roles |
|-------|-------|
| `/login` | public |
| `/chat` | requester, desk, supervisor |
| `/tickets` | desk, supervisor |
| `/cases/[id]` | desk, supervisor |
| `/supervisor` | supervisor |
| `/dashboard` | desk, supervisor |

## Demo scenarios

1. Login supervisor → Urdu food → Knowledge citation → Food ticket
2. Duplicate phone `03001234567` → HITL
3. Critical medical → HITL → approve → ticket
4. Case detail → timeline + Export PDF
5. Logout → citizen login (chat-only nav)

## Do not

- Hermes as orchestrator
- Skip Integrity or Knowledge on create path
- Open role switcher as auth source of truth (JWT is source of truth)
- WhatsApp / marketplace / Tier C unless judges demand
- Break Tier A/B E2E paths (tests use auth headers)
