# Deployment — Alkhidmat Relief Copilot

**Cross-chat contract:** Feature chats (Tier 1/2) must read this before changing ports, CORS, API paths, DB location, or env vars.

| Field | Value |
|-------|--------|
| **Target** | Alibaba Cloud **ECS** + Docker Compose |
| **Stack** | nginx → Next.js + FastAPI; SQLite + LangGraph checkpoints on volume |
| **Live URL** | *Pending — set after ECS public IP is known* |
| **Repo** | https://github.com/Atif1299/alkhidmat-relief-copilot |

---

## Architecture (live)

```
Browser  →  http://PUBLIC_IP
              nginx :80
                ├── /api/* , /health  →  api:8000 (FastAPI)
                └── /*                →  web:3000 (Next.js)
              volume relief_data
                ├── relief.db
                └── checkpoints.db   (durable HITL)
              DashScope Qwen (outbound HTTPS)
```

**Same-origin:** Frontend is built with `NEXT_PUBLIC_API_URL=""` so the browser calls `/api/v1/...` on the same host. Do not point the production UI at `localhost:8000`.

---

## What you authenticate (browser only)

Never paste Alibaba passwords or full API keys into chat.

| Step | Console | Return to deploy chat |
|------|---------|------------------------|
| 1 | https://www.alibabacloud.com/ — sign in / register | “Account ready” + **region** (prefer `ap-southeast-1` Singapore) |
| 2 | ECS → Create Instance | **Public IP**, instance ID, SSH username (`root` or `ubuntu`) |
| 3 | Security group | Ports **22**, **80** open (443 later for HTTPS) |
| 4 | SSH from your PC | Confirm login works |
| 5 | Server `.env` | Set `DASHSCOPE_API_KEY` on the VM only |

### ECS create checklist

- Image: **Ubuntu 22.04**
- Spec: **2 vCPU / 4 GiB** (minimum comfortable for Next + API)
- Network: assign **public IPv4**
- Security group inbound: TCP 22, 80 (and 443 when you add TLS)

---

## Local / server files

| Path | Role |
|------|------|
| [docker-compose.yml](../docker-compose.yml) | `api` + `web` + `nginx` |
| [backend/Dockerfile](../backend/Dockerfile) | FastAPI image |
| [frontend/Dockerfile](../frontend/Dockerfile) | Next.js image |
| [deploy/nginx.conf](../deploy/nginx.conf) | Reverse proxy + SSE timeouts |
| [deploy/ssh-up.sh](../deploy/ssh-up.sh) | `compose up --build` helper |
| [.env.production.example](../.env.production.example) | Env template (copy to `.env` on server) |

---

## Bring-up on ECS (after you have public IP)

SSH in, then:

```bash
# Docker (Ubuntu)
sudo apt-get update
sudo apt-get install -y ca-certificates curl git
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER
# log out/in if needed

git clone https://github.com/Atif1299/alkhidmat-relief-copilot.git
cd alkhidmat-relief-copilot
cp .env.production.example .env
nano .env   # set DASHSCOPE_API_KEY, LLM_MODE=qwen, keep CORS_ORIGINS=*

chmod +x deploy/ssh-up.sh
./deploy/ssh-up.sh
# or: docker compose up -d --build
```

### Smoke checklist

```bash
curl -s http://127.0.0.1/health
# expect: "tier":"B"

# From your laptop:
curl -s http://PUBLIC_IP/health
```

Browser:

1. `http://PUBLIC_IP/chat` — Urdu food path → Knowledge citations + ticket  
2. Duplicate phone `03001234567` → Supervisor → Approve (restart API container mid-wait should still resume)  
3. Case detail → timeline + Export PDF  
4. Role switcher still works  

Then update **Live URL** at the top of this file and commit.

### Redeploy after code push

```bash
cd ~/alkhidmat-relief-copilot   # or your clone path
git pull origin main
docker compose up -d --build
```

**Volume:** `relief_data` keeps SQLite + checkpoints across rebuilds. Do not `docker compose down -v` on production unless you intend to wipe demo data.

---

## Environment variables

| Var | Production |
|-----|------------|
| `LLM_MODE` | `qwen` |
| `DASHSCOPE_API_KEY` | server `.env` only |
| `DASHSCOPE_MODEL` | `qwen-plus` (or your Model Studio model) |
| `DASHSCOPE_BASE_URL` | intl or Beijing compatible-mode URL |
| `CORS_ORIGINS` | `*` (same-origin UI) or `http://PUBLIC_IP` |
| `DATABASE_URL` | set by compose to `/app/data/relief.db` |
| `CHECKPOINT_PATH` | `/app/data/checkpoints.db` |
| `NEXT_PUBLIC_API_URL` | **empty** at Docker build (same-origin) |

Local Next.js still defaults API to `http://localhost:8000` when env is unset.

---

## HITL durability

LangGraph uses **AsyncSqliteSaver** → `checkpoints.db` on the data volume.  
Case row stays in `relief.db` as `pending_hitl`. Approve/Reject after API restart works **if the volume was not deleted**.

---

## Next (not this cut)

1. Domain + HTTPS (Caddy / certbot / SLB)  
2. RDS Postgres (`DATABASE_URL`)  
3. GitHub Actions → SSH deploy  
4. Optional embeddings RAG (OpenSearch / pgvector)  

---

## For other Cursor chats

When changing the product:

- Keep nginx path `/api/` → FastAPI `/api/`  
- Persist DB under `/app/data` in Docker  
- Call `await init_graph()` at startup (already in `main.py` lifespan)  
- Update this file if live URL, ports, or env names change  
