# Deployment — Alkhidmat Relief Copilot

**Cross-chat contract:** Feature chats (Tier 1/2) must read this before changing ports, CORS, API paths, DB location, or env vars.

| Field | Value |
|-------|--------|
| **Target** | **GCP** project `x-saas-488416` — Cloud Run + Cloud SQL |
| **Region** | `asia-south1` |
| **Stack** | `relief-web` (Next.js) + `relief-api` (FastAPI) + Cloud SQL Postgres |
| **LLM** | Alibaba **DashScope / Qwen** (not hosted on GCP) |
| **Live API URL** | https://relief-api-4idrhaffca-el.a.run.app |
| **Live Web URL** | https://relief-web-4idrhaffca-el.a.run.app |
| **Repo** | https://github.com/Atif1299/alkhidmat-relief-copilot |

---

## Why not Alibaba ECS

Alibaba **ECS free trial was not eligible**; paid Subscription ECS was skipped.  
**Hosting = GCP.** **Brain (LLM) = Alibaba DashScope.**  
Pitch: *“LLM on Alibaba DashScope; app on Google Cloud Run.”*

Active plan copy: [.cursor/gcp_cloud_run_deploy.plan.md](../.cursor/gcp_cloud_run_deploy.plan.md)

---

## GCP services (this deploy)

| Service | Resource name | Purpose |
|---------|---------------|---------|
| Cloud Run | `relief-api` | FastAPI + LangGraph + SSE |
| Cloud Run | `relief-web` | Next.js UI |
| Artifact Registry | `relief` | Docker images |
| Cloud SQL | `relief-pg` | Postgres DB `aiddesk` |
| Secret Manager | `dashscope-api-key`, `db-password` | Secrets |
| Cloud Build | builds | Build/push images |

**Local Compose:** [docker-compose.yml](../docker-compose.yml) runs **`db` (Postgres/pgvector) + `api` + `web`**. SQLite is not the Tier 3 product target.

### Tier 3 promote checklist

1. Cloud SQL: enable `vector` extension (`CREATE EXTENSION vector;`).
2. Secret Manager: add `jwt-secret` (map to `JWT_SECRET` on Cloud Run).
3. Redeploy API/web via `deploy/gcp/03_build_and_deploy.sh`.
4. Confirm `/health` shows `"tier": "3"` and login works on live URL.
5. Reindex SOPs (startup embeds when `DASHSCOPE_API_KEY` set and chunks lack embeddings).

---

## Architecture (live)

```
Browser  →  https://relief-web-….run.app
              Next.js (NEXT_PUBLIC_API_URL → api)
         →  https://relief-api-….run.app
              FastAPI
                ├── Secret Manager (DashScope key)
                ├── Cloud SQL Postgres (cases + HITL checkpoints)
                └── outbound HTTPS → DashScope Qwen
```

---

## What you authenticate

Never paste GCP passwords or full API keys into chat.

| Step | Action | Return to deploy chat |
|------|--------|------------------------|
| 1 | `gcloud auth login` + `gcloud config set project x-saas-488416` | Confirm project `x-saas-488416` |
| 2 | [Console](https://console.cloud.google.com/) → Billing on `x-saas-488416` | “Billing enabled” |
| 3 | Create secret (local terminal, not chat): see below | “Secret created” |

### Create DashScope secret (run locally)

```bash
gcloud config set project x-saas-488416
# Pipe key from your local backend/.env — do not paste into Cursor chat
# Example: echo -n "YOUR_KEY" | gcloud secrets create dashscope-api-key --data-file=-
```

---

## Scripts

| Path | Role |
|------|------|
| [deploy/gcp/01_enable_apis.sh](../deploy/gcp/01_enable_apis.sh) | Enable GCP APIs |
| [deploy/gcp/02_bootstrap.sh](../deploy/gcp/02_bootstrap.sh) | Artifact Registry + Cloud SQL + secrets stubs |
| [deploy/gcp/03_build_and_deploy.sh](../deploy/gcp/03_build_and_deploy.sh) | Build images + deploy Cloud Run |
| [backend/Dockerfile](../backend/Dockerfile) | API image (`$PORT`) |
| [frontend/Dockerfile](../frontend/Dockerfile) | Web image (`$PORT`, build-arg API URL) |
| [.env.production.example](../.env.production.example) | Env template |

---

## Environment (Cloud Run api)

| Var | Value |
|-----|--------|
| `LLM_MODE` | `qwen` |
| `DASHSCOPE_API_KEY` | from Secret Manager |
| `DASHSCOPE_MODEL` | `qwen-plus` (or your Model Studio model) |
| `DASHSCOPE_BASE_URL` | Beijing MaaS compatible-mode (working): `https://ws-3fcwag66tpemo42e.cn-beijing.maas.aliyuncs.com/compatible-mode/v1` — **not** intl (401) |
| `DATABASE_URL` | Postgres via Cloud SQL socket (set by deploy script) |
| `JWT_SECRET` | from Secret Manager (`jwt-secret`) |
| `AUTH_DISABLED` | `false` |
| `DASHSCOPE_EMBEDDING_MODEL` | `text-embedding-v2` |
| `CORS_ORIGINS` | Web Cloud Run origin |
| `PORT` | Injected by Cloud Run |

Web image build-arg: `NEXT_PUBLIC_API_URL=https://<relief-api-url>`

---

## HITL durability

On GCP and local Compose, LangGraph uses the **Postgres checkpointer** when `DATABASE_URL` is Postgres.  
SQLite checkpointer is for automated tests / legacy only.

---

## Redeploy (after code push)

**Full (api + web + CORS refresh):**

```bash
# Git Bash / WSL from repo root
export DASHSCOPE_BASE_URL='https://ws-3fcwag66tpemo42e.cn-beijing.maas.aliyuncs.com/compatible-mode/v1'
bash deploy/gcp/03_build_and_deploy.sh
```

**API only (PowerShell):**

```powershell
gcloud builds submit backend --tag asia-south1-docker.pkg.dev/x-saas-488416/relief/api:latest
gcloud run deploy relief-api --image asia-south1-docker.pkg.dev/x-saas-488416/relief/api:latest --region asia-south1
```

**Web only:** rebuild after API URL known — `gcloud builds submit` with `deploy/gcp/cloudbuild.web.yaml`, then `gcloud run deploy relief-web …`.

**Feature chats:** after changing API contracts or env names, update this file and redeploy both services if `NEXT_PUBLIC_API_URL` or CORS must change. Do **not** reset `DASHSCOPE_BASE_URL` to intl.

---

## Smoke checklist

```bash
curl -s https://relief-api-4idrhaffca-el.a.run.app/health
# expect: "tier":"3", "auth_required":true
```

Browser on **https://relief-web-4idrhaffca-el.a.run.app**:

1. `/login` as `supervisor@aiddesk.example` / `AidDesk!2026`
2. `/chat` — Urdu food → Knowledge citations + ticket  
3. Duplicate `03001234567` / critical medical → Supervisor → Approve  
4. Case detail → timeline + Export PDF  
5. Logout → login as `citizen@aiddesk.example` — chat-only nav  

**Reindex SOPs on Cloud SQL (optional one-off):**

```bash
# from a shell with DATABASE_URL + DASHSCOPE_API_KEY
cd backend && python -m app.tools.reindex_sops --force
```

---

## Later (not this cut)

1. Custom domain on Cloud Run  
2. `min-instances=1` on demo day  
3. GitHub Actions → Cloud Build  
4. WhatsApp / Alkhidmat ERP connectors (Tier C)  
