# Tier Reference — synced with docs/PRODUCT_DEFINITION.md

## Tier A (implement first)

| ID | Feature | Acceptance |
|----|---------|------------|
| A1 | Citizen chat Urdu+EN | Streaming agent trace |
| A2 | LangGraph 6-agent pipeline | Integrity never skipped |
| A3 | HITL supervisor | approve/reject resumes graph |
| A4 | Duplicate detection | Same phone flagged |
| A5 | Resource matching | Lahore seed by category |
| A6 | Ticket lifecycle | pending_hitl → open → dispatched |
| A7 | Dashboard metrics | cases, time-to-ticket, escalation % |
| A8 | Audit log | agent steps + supervisor decisions |
| A9 | Qwen/DashScope | real LLM with mock fallback |
| A10 | Demo scenarios | 3 E2E tests pass |

## Tier B (after Tier A green)

| ID | Feature |
|----|---------|
| B8 | Light RAG / SOP Knowledge agent (UI-visible retrieval) |
| B9 | Role views: Requester / Desk / Supervisor |
| B10 | Case timeline UI |
| B11 | Richer Lahore district seed |
| B12 | PDF case export |

## Tier C (defer)

WhatsApp prod, real Alkhidmat API, mobile apps, 10+ agents, billing, CNIC OCR main feature.

## Stack

LangGraph + FastAPI + Next.js 14 + SQLite + Qwen. Repo: github.com/Atif1299/alkhidmat-relief-copilot
