# `.cursor/` — teammate guide

Commit this folder with the repo so every Cursor/agent session shares the same product rules and tier plans.

## Tier plans (read in order)

| File | Tier | Status |
|------|------|--------|
| [tier_1_core_aid_desk.plan.md](./tier_1_core_aid_desk.plan.md) | Tier 1 / A — Core aid desk | Complete |
| [tier_2_knowledge_ops.plan.md](./tier_2_knowledge_ops.plan.md) | Tier 2 / B — Knowledge, timeline, PDF, roles UI | Complete |
| [tier_3_production_hardening_e2d44f61.plan.md](./tier_3_production_hardening_e2d44f61.plan.md) | Tier 3 — JWT, Postgres/pgvector, vector RAG | Complete (local-first) |

## Deploy plans (separate chats)

| File | Purpose |
|------|---------|
| [gcp_cloud_run_deploy.plan.md](./gcp_cloud_run_deploy.plan.md) | Live hosting on GCP Cloud Run + Cloud SQL |
| [alibaba_ecs_deploy_cce6348d.plan.md](./alibaba_ecs_deploy_cce6348d.plan.md) | Alibaba ECS attempt (superseded by GCP for hosting) |

## Rules & skills

- `rules/` — product + stack locks (`alkhidmat-core`, LangGraph backend, Next.js frontend)
- `skills/alkhidmat-build/` — how to implement tiers
- `skills/hackathon-mentor/` — scope / judging discipline

## Source of truth

- Product tiers: `docs/PRODUCT_DEFINITION.md`
- Quick table: `skills/alkhidmat-build/tier-reference.md`
- Repo: https://github.com/Atif1299/alkhidmat-relief-copilot

**Do not commit:** `.cursor/projects/` (local only; gitignored).
