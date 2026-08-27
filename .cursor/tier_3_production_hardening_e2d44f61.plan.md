---
name: Tier 3 Production Hardening
overview: "Local-first Production Hardening (user choice 1D): Docker Postgres as the only target DB, real JWT auth with API-enforced roles, then DashScope embeddings + pgvector for Knowledge RAG—keeping citations UI—then redeploy to existing GCP Cloud Run/Cloud SQL. WhatsApp and other Tier C items stay deferred."
todos:
  - id: docs-tier3
    content: "Docs/Cursor: add Tier 3 Production Hardening; retire SQLite as target; WhatsApp deferred — commit + push"
    status: pending
  - id: docker-postgres
    content: "Compose: pgvector/Postgres service; local DATABASE_URL + seed/checkpointer on Postgres — commit + push"
    status: pending
  - id: jwt-auth-api
    content: "Backend: users table, JWT login/me, role dependencies on APIs — commit + push"
    status: pending
  - id: frontend-auth
    content: "Frontend: login page, Bearer client, role from JWT — commit + push"
    status: pending
  - id: pgvector-rag
    content: pgvector column + DashScope embed index + vector search_sops with keyword fallback — commit + push
    status: pending
  - id: tests-demo
    content: Tests for auth gates + RAG modes; update DEMO_SCRIPT — commit + push
    status: pending
  - id: gcp-promote
    content: "GCP: JWT secret, Cloud SQL vector ext, reindex, redeploy Cloud Run — commit + push docs/URL"
    status: pending
isProject: false
---

# Tier 3 — Production Hardening (Local-first → GCP)

## Locked choices (from you + mentor)

| Decision | Lock |
|----------|------|
| Track | **1D** — Auth + Docker Postgres first, then vector RAG |
| WhatsApp / Twilio | **Defer** (not in this tier) |
| SQLite as product DB | **Retire as target** — local Compose uses Postgres; SQLite only if someone runs old `.env` by mistake |
| Agent marketplace / 10+ agents | **Out of scope** |
| Live hosting after local green | Existing GCP: Cloud Run + Cloud SQL `relief-pg` + DashScope |

**Product stance:** Current Tier A+B is already presentable. Tier 3 makes it **production-shaped** (real roles, real DB, real semantic RAG)—not a second demo toy.

---

## Target architecture

```mermaid
flowchart TB
  subgraph local [Local Docker Compose]
    Web[Nextjs]
    Api[FastAPI]
    Pg["Postgres + pgvector"]
    Web --> Api
    Api --> Pg
    Api --> DS[DashScope Qwen + Embeddings]
  end
  subgraph gcp [GCP after promote]
    CRW[Cloud Run relief-web]
    CRA[Cloud Run relief-api]
    SQL["Cloud SQL + pgvector"]
    SM[Secret Manager]
    CRW --> CRA
    CRA --> SQL
    CRA --> SM
    CRA --> DS
  end
```

Graph stays:

`Intake → Triage → Knowledge → Integrity → HITL? → Matcher → Dispatch`

Knowledge retrieval becomes **vector (pgvector) + keyword fallback**; UI `SopCitations` unchanged in shape.

---

## Phase 1 — Docker Postgres + JWT auth (do first)

### 1A. Local Postgres in Compose

- Add service `db` to [docker-compose.yml](docker-compose.yml): image `pgvector/pgvector:pg16`, volume, port `5432`, DB `aiddesk`.
- Default local `DATABASE_URL` → `postgresql+psycopg://aiddesk:aiddesk@localhost:5432/aiddesk` (document in [.env.example](.env.example)).
- Seed + migrations path must work on Postgres (already mostly via `is_postgres` in [backend/app/config.py](backend/app/config.py) / [session.py](backend/app/db/session.py)).
- Checkpointer continues on Postgres (`AsyncPostgresSaver`) when `DATABASE_URL` is Postgres.
- Update [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) + [docs/DECISIONS.md](docs/DECISIONS.md): SQLite no longer the Tier 3 target.

### 1B. Auth model (concrete)

- Seeded users (no OAuth for this tier):

| Email (demo) | Role | Use |
|--------------|------|-----|
| `citizen@aiddesk.example` | `requester` | Chat only |
| `desk@aiddesk.example` | `desk` | Tickets, cases, dashboard, PDF |
| `supervisor@aiddesk.example` | `supervisor` | HITL decide + desk views |

- Passwords hashed with **bcrypt**; issue **JWT** (`ACCESS_TOKEN` HS256, secret from env).
- New tables: `users` (`id`, `email`, `password_hash`, `role`, `active`).
- Endpoints: `POST /api/v1/auth/login`, `GET /api/v1/auth/me`.
- FastAPI dependencies: `require_user`, `require_roles(...)`.
- Protect:
  - `requester`: `POST /chat`, `GET` own cases if we scope by creator later (v1: chat + read ticket by id after create)
  - `desk`: cases list/detail/timeline/export/metrics
  - `supervisor`: queue + decide (+ desk reads)
- Frontend: login page; store JWT; send `Authorization: Bearer`; replace open [roles.ts](frontend/lib/roles.ts) switcher as **source of truth** with JWT role (optional “switch user” = logout + login as other seeded user for demo).

Commit cadence: `feat(infra): docker postgres pgvector` → `feat(auth): JWT users and API role gates` → `feat(frontend): login and bearer client`.

---

## Phase 2 — Vector RAG (pgvector)

### 2A. Schema + embed

- Extend `sop_chunks` with `embedding` column (`vector(dim)` — use DashScope embedding model dimension as implemented, e.g. text-embedding compatible size documented in code).
- Enable `CREATE EXTENSION IF NOT EXISTS vector` on startup/migrate for Postgres.
- At index time ([sops.py](backend/app/tools/sops.py)): embed each chunk via DashScope embeddings API; store vector.
- Re-index script/flag: `python -m app.tools.reindex_sops` or seed hook.

### 2B. Retrieval

- `search_sops`: **cosine / L2 over pgvector** filtered by category when present; if embed fails or empty vectors → **existing keyword** path (no broken Knowledge).
- Knowledge node + SSE + citations: same `sop_hits` shape (`title`, `category`, `excerpt`, `score`).
- Optional: store `retrieval_mode: vector|keyword` in trace detail for judges.

### 2C. Tests

- Unit/integration: vector hit returns SOP; keyword fallback still works; auth blocks anonymous supervisor decide.

Commit: `feat(rag): pgvector embeddings for Knowledge agent`.

---

## Phase 3 — Promote to GCP

- Enable `vector` on Cloud SQL `relief-pg` (pgvector-supported Postgres version; adjust instance flags if needed).
- Re-run embed index against Cloud SQL (one-off job or API startup if empty).
- Redeploy via [deploy/gcp/03_build_and_deploy.sh](deploy/gcp/03_build_and_deploy.sh); secrets already hold DashScope key; add `JWT_SECRET` to Secret Manager.
- Smoke: login as supervisor on live URL → HITL → PDF; Knowledge shows vector retrieval in trace.

Commit: `docs: Tier 3 auth+pgvector deploy notes` + deploy.

---

## Explicitly out of this tier

- Full WhatsApp/Twilio production  
- Real Alkhidmat API login  
- Mobile native apps  
- Agent marketplace / 10+ agents  
- Stripe / multi-org billing  
- CNIC OCR  

(Slide line OK: “Channels and Alkhidmat ERP connectors — roadmap.”)

---

## Docs / Cursor sync (first commit)

- [docs/PRODUCT_DEFINITION.md](docs/PRODUCT_DEFINITION.md): add **Tier 3 — Production Hardening** (auth, Postgres-only target, pgvector RAG); keep Tier C deferred list.
- [.cursor/skills/alkhidmat-build](.cursor/skills/alkhidmat-build/SKILL.md) + tier-reference: Tier 3 after B green.
- [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md): local Compose = Postgres; GCP promote steps for JWT + pgvector.

---

## Acceptance (Tier 3 done)

- [ ] `docker compose up` runs api + web + **Postgres/pgvector** (no SQLite required)
- [ ] Unauthenticated `POST /supervisor/.../decide` → **401/403**
- [ ] Login as each seeded role; nav + API match permissions
- [ ] Knowledge agent retrieves via **vector** when embeddings present; citations still show
- [ ] Tier A/B E2E paths still pass with auth headers in tests
- [ ] Live GCP redeployed; `/health` still ok; demo login works on public URL

---

## Implementation todos (each ends with commit + push)

Ordered for a Tier 3 split chat to execute after plan approval.
