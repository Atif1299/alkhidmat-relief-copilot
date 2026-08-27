# Deployment — Alkhidmat Relief Copilot

**Cross-chat contract:** Feature chats (Tier 1/2) must read this before changing ports, CORS, API paths, DB location, or env vars.

| Field | Value |
|-------|--------|
| **Target** | **GCP** project `x-saas` — Cloud Run + Cloud SQL |
| **Region** | `asia-south1` |
| **Stack** | `relief-web` (Next.js) + `relief-api` (FastAPI) + Cloud SQL Postgres |
| **LLM** | Alibaba **DashScope / Qwen** (not hosted on GCP) |
| **Live API URL** | *Pending — set after first Cloud Run deploy* |
| **Live Web URL** | *Pending — set after first Cloud Run deploy* |
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

**Local only:** [docker-compose.yml](../docker-compose.yml) still runs nginx + SQLite for laptop demos — **not** used on GCP.

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
| 1 | `gcloud auth login` + `gcloud config set project x-saas` | Confirm project `x-saas` |
| 2 | [Console](https://console.cloud.google.com/) → Billing on `x-saas` | “Billing enabled” |
| 3 | Create secret (local terminal, not chat): see below | “Secret created” |

### Create DashScope secret (run locally)

```bash
gcloud config set project x-saas
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
| `DASHSCOPE_BASE_URL` | working intl/Beijing compatible-mode URL |
| `DATABASE_URL` | Postgres via Cloud SQL socket (set by deploy script) |
| `CORS_ORIGINS` | Web Cloud Run origin |
| `PORT` | Injected by Cloud Run |

Web image build-arg: `NEXT_PUBLIC_API_URL=https://<relief-api-url>`

---

## HITL durability

On GCP, LangGraph uses **Postgres checkpointer** on Cloud SQL (same DB).  
Local Compose still uses SQLite `checkpoints.db`.

---

## Redeploy (after code push)

```bash
# From repo root, project x-saas, region asia-south1
bash deploy/gcp/03_build_and_deploy.sh
```

Or rebuild only api/web as documented in the script comments.

**Feature chats:** after changing API contracts or env names, update this file and redeploy both services if `NEXT_PUBLIC_API_URL` or CORS must change.

---

## Smoke checklist

```bash
curl -s https://API_URL/health
# expect: "tier":"B"
```

Browser on **Web URL**:

1. `/chat` — Urdu food → Knowledge citations + ticket  
2. Duplicate `03001234567` → Supervisor → Approve  
3. Case detail → timeline + Export PDF  
4. Role switcher  

Then set **Live API URL** / **Live Web URL** at the top of this file and commit.

---

## Later (not this cut)

1. Custom domain on Cloud Run  
2. `min-instances=1` on demo day  
3. GitHub Actions → Cloud Build  
4. Optional pgvector / embeddings RAG  
