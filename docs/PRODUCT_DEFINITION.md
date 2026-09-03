# Product Definition — Alkhidmat Relief Copilot

**Locked:** 2026-08-23 (Mentor)  
**Source of truth for pitch, demo, and build**

---

## What this product IS

**One sentence:**  
An **agentic operations desk for relief NGOs** that turns a messy Urdu/English aid request into a **verified, prioritized, resource-matched ticket** — with a human in the loop for high-risk cases.

**Category:** B2B / NGO **workflow SaaS** (aid desk), *not* a consumer chatbot and *not* “just a Copilot sidebar.”

| Label people use | Accurate? | Better framing |
|------------------|-----------|----------------|
| Chatbot | No | Multi-agent **case desk** |
| Simple Copilot | Weak | **Aid Desk OS** — agents do triage/match/dispatch |
| Full SaaS | Yes (demo-scale) | Multi-tenant NGO ops product *prototype* |
| WhatsApp bot only | No (optional later) | Web desk first; channel can expand |

**Who uses it**

| Role | What they do |
|------|----------------|
| **Citizen / requester** | Submits need in Urdu or English |
| **Ops / volunteer desk** | Sees tickets, agent trace, matches |
| **Supervisor** | Approves critical / high-risk cases |

**Winning signal (from training playbook):**  
The desk operator (and requester) **knows what happens next** — ticket ID, category, matched resource, or “waiting for supervisor.” The citizen can leave and **check status later** with that AKD number plus the phone they gave (no account).

---

## What problem we solve (Listen → Focus)

**One user:** Alkhidmat-style field/ops desk officer (and the citizen requesting help).  
**One pain:** Aid requests arrive messy (Urdu/English, incomplete, duplicate, wrong category) → slow routing, wasted packs, missed critical medical cases.  
**One moment:** The **first 60 seconds after a request arrives** — classify, verify, match, open ticket (or escalate).

**Promise (Focus):**  
“From free-text request → verified ticket + next action in under a minute.”

---

## What we submitted vs what we can enhance

Registration only locked the **idea + name + short detail**. Architecture, stack, and UI were **not** locked. Enhancements are allowed if they still match that short detail.

**Must still match:** multi-agent, Urdu/English, triage categories, duplicate/fraud, resource match, dispatch ticket, human supervisor, measurable handling.

---

## Mapped to official training slides

| Slide principle | Our product |
|-----------------|-------------|
| Solve what is real | Real NGO desk pain: routing + duplicates + critical cases |
| Learn by building | Thin working prototype: chat → ticket E2E |
| Make impact visible | Dashboard: cases, time-to-ticket, % escalated |
| Not most complicated | 4–6 agents rock-solid > 12 half-agents + RAG theater |
| One-minute explain | “Request in → agents verify & match → ticket or human approve” |
| Winning signal | User/desk knows **next action** |

---

## Core stack (target)

| Layer | Choice | Why judges / industry |
|-------|--------|------------------------|
| Orchestration | LangGraph multi-agent | True agentic (not one LLM call) |
| LLM | Qwen via DashScope / Qoder | Alibaba Cloud story |
| API | FastAPI | Clean backend for SaaS path |
| DB | SQLite → Postgres-ready | Cases, resources, volunteers |
| UI | Next.js/React — Chat + Supervisor + Dashboard | Industry-feel ops product |
| Tools | MCP-style tool contracts | Matches Qoder Skills/MCP training |
| Optional cloud | OSS (docs), ECS/FC deploy | Architecture slide |

---

## Enhancement tiers (Mentor ranked)

### Tier A — Must (industry-feel + win)

1. Visible **agent pipeline / trace** in UI  
2. **HITL supervisor** queue (approve/reject)  
3. **Duplicate + critical** demo paths  
4. **Metrics dashboard** (time-to-ticket, cases, escalations)  
5. **Urdu + English** live  
6. **Qwen/DashScope** wired for real LLM calls  
7. Audit log (who approved what, when)

### Tier B — High value if Tier A done (powerful but focused)

8. **Knowledge / light RAG** — Alkhidmat-style SOPs, category rules (show retrieval in UI)  
9. Role-based views: Requester vs Desk vs Supervisor  
10. Case status timeline (Requested → Matched → Dispatched → Closed)  
11. Seed “Lahore district” inventory that feels real  
12. Export case report / PDF summary for ops  

### Tier 3 — Production Hardening (local-first → GCP)

13. **Docker Postgres + pgvector** as the target DB (SQLite retired for product work)  
14. **JWT auth** with API-enforced roles (`requester` / `desk` / `supervisor`)  
15. **Vector RAG** — DashScope embeddings + pgvector / cosine; keyword fallback  
16. Keep durable HITL checkpointer on Postgres; redeploy Cloud Run when local green  

### Tier C — Defer (looks big, weak demo ROI)

- Full WhatsApp/Twilio production  
- Real Alkhidmat API login  
- Mobile native apps  
- 10+ agents / full agent marketplace  
- Multi-org billing / Stripe SaaS billing  
- Computer vision CNIC OCR (unless OSS photo upload stub only)

---

## SaaS narrative for judges (without overbuilding)

Position as: **“Relief Ops SaaS — Aid Desk module”**

Demo = one NGO workspace (Alkhidmat Lahore).  
Future (say on slide, don’t build): multi-org, WhatsApp channel, real inventory APIs.

That reads **industry usable** without building a full commercial SaaS in 6 days.

---

## One-minute pitch (memorize)

> Aid requests hit NGOs as messy Urdu and English messages. Alkhidmat Relief Copilot is a multi-agent aid desk: Intake extracts the need, Triage classifies it, Integrity catches duplicates and risk, Matcher finds stock or volunteers, Dispatch opens a ticket — and a Supervisor approves critical cases. Result: faster match, fewer frauds, measurable time-to-ticket — built on Alibaba Cloud Qwen.
