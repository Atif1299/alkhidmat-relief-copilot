# GCP Cloud Run Deploy — active plan

Canonical execution plan for live hosting. Full detail also in Cursor plan history; **this file** is the in-repo pointer for other chats.

## Locked

| Item | Value |
|------|--------|
| Project | `x-saas-488416` |
| Region | `asia-south1` |
| Hosting | Cloud Run `relief-api` + `relief-web` |
| DB | Cloud SQL Postgres `relief-pg` / DB `aiddesk` |
| LLM | Alibaba DashScope (Secret Manager) |
| Not used | Alibaba ECS (free trial ineligible) |

## Contract

See [docs/DEPLOYMENT.md](../docs/DEPLOYMENT.md).

## Scripts

`deploy/gcp/01_enable_apis.sh` → `02_bootstrap.sh` → `03_build_and_deploy.sh`
