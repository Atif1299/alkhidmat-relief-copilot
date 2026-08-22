# Alkhidmat Relief Copilot — Agent System

This file defines **two layers** of agents:

1. **Product agents** — the multi-agent AI desk we build and demo
2. **Cursor workflow agents** — how we work in this repo to win the hackathon

---

## Product agents (what we ship)

| Agent | Role | Tools | Output |
|-------|------|-------|--------|
| **Intake** | Language detect, extract need/location/urgency/contact | — | Structured case draft |
| **Triage** | Classify: Food, Medical, Shelter, Blood, Education, Other | — | Category + priority |
| **Integrity** | Duplicate phone/CNIC/area; fraud heuristics | `search_similar_cases` | Risk score |
| **Resource Matcher** | Match inventory, camps, blood banks, volunteers | `list_resources` | Matched resource(s) |
| **Dispatch** | Create ticket, assign volunteer, notify requester | `create_case`, `assign_volunteer`, `send_status_message` | Ticket ID |
| **Supervisor (HITL)** | Approve/reject critical or high-risk cases | `escalate_to_human` | Approved / rejected |

**Orchestrator:** LangGraph (not Hermes) — routes between agents, never skips Integrity on create. HITL interrupt for critical/high-risk.

**Repo:** https://github.com/Atif1299/alkhidmat-relief-copilot.git

**Build order:** Tier A (`docs/PRODUCT_DEFINITION.md`) complete before Tier B.

### Optional v2 (only if judges / emails demand it)

| Agent | Role | When to add |
|-------|------|-------------|
| **Knowledge (RAG)** | SOPs, camp policies, blood-type rules, Urdu FAQs | Evaluation rewards domain knowledge / accuracy |
| **Analytics** | Summarize metrics for dashboard | Evaluation rewards measurable impact |

**Rule:** Ship 4–6 product agents rock-solid before adding more.

---

## Cursor workflow agents (how we build)

Use these modes when working in this repo. In chat, invoke by name: *"Act as Mentor"* or *"Act as Architect"*.

### 1. Mentor (primary — default for you)

**Purpose:** Win the hackathon, not build everything.

**Responsibilities:**
- Map every feature to **evaluation criteria** (see `docs/EVALUATION_CRITERIA.md`)
- Say **no** to scope creep unless it clearly increases score
- Maintain pitch: mission fit + agentic + Urdu/English + Alibaba Cloud + demo impact
- Log decisions in `docs/DECISIONS.md`
- Update plan after each organizer email

**Output format:** Problem → Recommendation → Why judges care → Build cost (S/M/L)

---

### 2. Architect

**Purpose:** Technical design before code.

**Responsibilities:**
- LangGraph graph, state schema, tool contracts
- Alibaba Cloud mapping (DashScope/Qwen, OSS, ECS/Function Compute)
- API + DB schema
- RAG design **only if** Mentor approved it

**Output:** Diagrams, file layout, interface list — no implementation unless asked.

---

### 3. Implementer

**Purpose:** Write code when user says **"start build"** or names a milestone.

**Responsibilities:**
- FastAPI backend, React/Next.js UI, LangGraph orchestrator
- Seed data (Lahore), tests for happy path + duplicate + escalation
- README, env example, deploy notes

**Constraints:** Match Architect design; no new agents without Mentor sign-off.

---

### 4. Demo & Pitch

**Purpose:** 3-minute demo, slides, judge Q&A.

**Responsibilities:**
- Demo script (Urdu + English scenarios)
- 5-slide deck outline
- Architecture slide with Alibaba Cloud
- FAQ: safety, fraud, HITL, scalability

**Trigger:** After core E2E works, or when submission deadline nears.

---

## Subagent usage (Cursor Task tool)

During implementation, delegate in parallel when useful:

| Subagent | Use when |
|----------|----------|
| **explore** | Find patterns, existing code, dependency versions |
| **shell** | Install deps, run servers, migrations |
| **generalPurpose** | Isolated feature slice (e.g. supervisor UI only) |

Do **not** spawn subagents for Mentor decisions — those stay in main thread with full hackathon context.

---

## Current phase

**Phase 1 — Build** (22–27 Aug 2026)

- [x] Product brief, agent system, skills, rules
- [x] Emails 1–3 logged → `docs/EMAIL_LOG.md`
- [ ] Qoder access confirmed (issued 21 Aug)
- [ ] Official submission format + rubric email
- [ ] Core MVP (see `docs/HACKATHON_MASTER_PLAN.md`)
- [ ] Regional demo ready (28–30 Aug, Lahore TBA)

**Phase 2 — Regional** (28–30 Aug) → **Phase 3 — Finale prep** (if finalist, 10 Sep)

---

## One-line pitch (keep everywhere)

> A multi-agent AI desk that turns an aid request (Urdu/English) into a verified, routed relief ticket — with human approval for high-risk cases.
