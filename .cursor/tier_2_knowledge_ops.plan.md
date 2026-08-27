---
name: Tier 2 Knowledge Ops
overview: "Tier B / Tier 2 — after Tier A E2E green: Knowledge SOP node + citations UI, role views, case timeline, richer Lahore seed, PDF export. Keyword RAG only (vector in Tier 3)."
todos:
  - id: docs-lock
    content: Lock Tier B architecture in docs + Cursor skills
    status: completed
  - id: seed-sops
    content: Expand Lahore inventory (≥25 resources) + SOP markdown corpus
    status: completed
  - id: knowledge-node
    content: Knowledge agent after Triage; search_sops keyword retrieval; sop_hits in state/API
    status: completed
  - id: timeline
    content: Case timeline API + /cases/[id] stages
    status: completed
  - id: pdf
    content: PDF export endpoint + UI button
    status: completed
  - id: roles-ui
    content: Requester / desk / supervisor views (localStorage role switcher pre-JWT)
    status: completed
  - id: tests
    content: Tier A E2E still pass; Knowledge/timeline/PDF covered
    status: completed
isProject: false
---

# Tier 2 — Knowledge & Ops Polish (Tier B)

**Also called:** Tier B in `docs/PRODUCT_DEFINITION.md`  
**Status:** Complete before Tier 3

## Prerequisite

Tier 1 / Tier A E2E green (happy path, duplicate, HITL).

## Graph (updated)

```
Intake → Triage → Knowledge → Integrity → Matcher → Dispatch
                         ↓ (critical OR high risk)
                    HITL interrupt → Supervisor
```

**Non-negotiable:** Integrity never skipped. Knowledge sits after Triage, before Integrity.

## Scope (B8–B12)

| ID | Feature | Acceptance |
|----|---------|------------|
| B8 | Knowledge + SOP citations | Trace includes Knowledge; UI shows Sources/SOPs |
| B9 | Role-based views | Requester = chat; desk = tickets/dashboard; supervisor = HITL |
| B10 | Case timeline | Requested → … → Dispatched stages on case detail |
| B11 | Richer Lahore seed | ≥25 resources + SOP corpus under `backend/app/knowledge/sops/` |
| B12 | PDF export | `GET /api/v1/cases/{id}/export.pdf` + UI |

## RAG stance (this tier)

**Keyword** retrieval over `sop_chunks` — intentional, not “broken RAG.”  
Vector / pgvector / DashScope embeddings → **Tier 3**.

## Auth stance (this tier)

Open role switcher via localStorage for demo.  
Real JWT + API gates → **Tier 3**.

## Out of scope

JWT, Docker Postgres target, embeddings → Tier 3  
WhatsApp / ERP / 10+ agents → Tier C

## Teammate notes

- Implement only B8–B12; do not start Tier C.  
- Keep Tier A demos green after every change.
