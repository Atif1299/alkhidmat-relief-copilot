# Tier Reference — synced with docs/PRODUCT_DEFINITION.md

## Tier A (complete)

| ID | Feature | Acceptance |
|----|---------|------------|
| A1–A10 | Core desk | E2E happy / duplicate / HITL |

## Tier B (complete)

| ID | Feature | Acceptance |
|----|---------|------------|
| B8–B12 | Knowledge, roles UI, timeline, seed, PDF | Citations + timeline + PDF |

## Tier 3 — Production Hardening (in progress)

| ID | Feature | Acceptance |
|----|---------|------------|
| T3-13 | Docker Postgres + pgvector | `docker compose up db` |
| T3-14 | JWT auth + API roles | Anonymous decide → 401; citizen decide → 403 |
| T3-15 | Vector RAG + keyword fallback | Knowledge trace shows `vector` or `keyword` |
| T3-16 | GCP promote | Live login + `/health` tier 3 |

## Tier C (defer)

WhatsApp prod, real Alkhidmat API, mobile apps, 10+ agents, billing, CNIC OCR.

## Graph

`Intake → Triage → Knowledge → Integrity → Matcher → Dispatch` (+ HITL)

## Stack

LangGraph + FastAPI + Next.js 14 + **Postgres/pgvector** + DashScope (Qwen + embeddings) + JWT.  
Repo: github.com/Atif1299/alkhidmat-relief-copilot
