# Tier Reference — synced with docs/PRODUCT_DEFINITION.md

## Tier A (complete)

| ID | Feature | Acceptance |
|----|---------|------------|
| A1 | Citizen chat Urdu+EN | Streaming agent trace |
| A2 | LangGraph pipeline | Integrity never skipped |
| A3 | HITL supervisor | approve/reject resumes graph |
| A4 | Duplicate detection | Same phone flagged |
| A5 | Resource matching | Lahore seed by category |
| A6 | Ticket lifecycle | pending_hitl → open → dispatched |
| A7 | Dashboard metrics | cases, time-to-ticket, escalation % |
| A8 | Audit log | agent steps + supervisor decisions |
| A9 | Qwen/DashScope | real LLM with mock fallback |
| A10 | Demo scenarios | 3 E2E tests pass |

## Tier B (in progress — after Tier A green)

| ID | Feature | Acceptance |
|----|---------|------------|
| B8 | Light RAG / SOP Knowledge agent | Knowledge in agent_trace; citations in UI |
| B9 | Role views | Switcher requester/desk/supervisor; nav gated |
| B10 | Case timeline | `GET .../timeline` + `/cases/[id]` ladder |
| B11 | Richer Lahore seed | ≥25 resources; SOP corpus indexed |
| B12 | PDF case export | `GET .../export.pdf` returns PDF |

## Tier C (defer)

WhatsApp prod, real Alkhidmat API, mobile apps, 10+ agents, billing, CNIC OCR main feature.

## Graph (Tier B)

`Intake → Triage → Knowledge → Integrity → Matcher → Dispatch` (+ HITL gate)

## Stack

LangGraph + FastAPI + Next.js 14 + SQLite + Qwen + reportlab.  
Repo: github.com/Atif1299/alkhidmat-relief-copilot
