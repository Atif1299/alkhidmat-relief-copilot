# Alkhidmat Relief Copilot — Hackathon Brief

**Event:** Alibaba Cloud AI Hackathon Pakistan (Bano Qabil / Alkhidmat)  
**Goal:** Top position via Agentic AI + social impact + Alibaba Cloud  
**Builder:** Muhammad Atif  
**Mode:** Individual (unless you add a teammate)

---

## One-line pitch

A multi-agent AI desk that turns an aid request (Urdu/English) into a verified, routed relief ticket — with human approval for high-risk cases.

---

## Registration fields (paste)

**Project Name:**  
`Alkhidmat Relief Copilot — Multi-Agent Aid Desk`

**Focus Area:**  
Pick closest to: AI / Artificial Intelligence / Social Impact / Cloud AI (whatever the dropdown offers)

**Short Detail (use this):**  
```
Alkhidmat Relief Copilot is an Agentic AI system that helps citizens and volunteers request and coordinate aid in Urdu and English. Multiple specialized agents triage the need (food, medical, shelter, blood, education), check for duplicates/fraud signals, match available resources, and create a dispatch ticket. High-risk cases escalate to a human supervisor. Built for real NGO workflows, not chat demos — with measurable time-to-match and case handling.
```

**Status:** Student / Final year (or Professional — use what fits the form)  
**Participation Type:** Individual  
**Province / City:** Punjab / Lahore  
**Age group:** from DOB 21/08/2003  
**Gender:** Male  
**CNIC:** your real CNIC  
**Phone / Email:** +92 323 4065995 / ranaatif1299@gmail.com (or matif65995)

---

## Why this can win

1. **Mission fit** — Alkhidmat = relief / social service  
2. **Truly agentic** — orchestrator + specialist agents + tools + HITL (not one chatbot)  
3. **Local** — Urdu + English  
4. **Cloud story** — Alibaba Cloud LLM + storage + hosting  
5. **Demo in 3 minutes** — one live request → ticket + dashboard metric  

---

## Agent architecture

```
User (Web / WhatsApp-style chat)
        ↓
[1] Intake Agent          — language detect, extract need, location, urgency, contact
        ↓
[2] Triage Agent          — classify: Food | Medical | Shelter | Blood | Education | Other
        ↓
[3] Integrity Agent       — duplicate phone/CNIC/location; basic fraud heuristics
        ↓
[4] Resource Matcher      — match to mock inventory / camps / blood banks / volunteers
        ↓
[5] Dispatch Agent        — create ticket, assign volunteer/org unit, notify
        ↓
[6] Supervisor (HITL)     — approve if urgency=critical OR integrity risk=high
```

**Orchestrator:** LangGraph (or LangChain) supervisor that calls tools and routes between agents.

---

## Tools each agent needs (keep simple)

| Tool | Purpose |
|------|---------|
| `create_case(payload)` | Save case to DB |
| `search_similar_cases(phone, area)` | Duplicate check |
| `list_resources(category, city)` | Mock inventory |
| `assign_volunteer(case_id)` | Assign from volunteer list |
| `escalate_to_human(case_id, reason)` | HITL queue |
| `send_status_message(user, text)` | Confirmation to requester |

Use **SQLite or Postgres** + seed data (Lahore camps, blood banks, food packs). No need for real Alkhidmat API in v1.

---

## Alibaba Cloud angle (say this on the slide)

- **Model:** Alibaba Cloud Model Studio / DashScope (Qwen) for Urdu+English  
- **Storage:** OSS for uploaded CNIC/docs photos (optional)  
- **Compute:** ECS or Function Compute for API  
- **Fallback if account slow:** run Qwen-compatible API locally for demo, architecture slide still shows Alibaba Cloud target deploy  

---

## 48-hour build plan

### Day 1 (core)
- [ ] FastAPI backend + simple Next.js/React chat UI  
- [ ] LangGraph orchestrator with 4 agents minimum (Intake, Triage, Integrity, Dispatch)  
- [ ] Seed DB: 20 resources, 10 volunteers, 5 duplicate test cases  
- [ ] English path working end-to-end  

### Day 2 (win polish)
- [ ] Urdu prompts / sample Urdu queries  
- [ ] Supervisor approval screen (approve / reject critical cases)  
- [ ] Dashboard: cases today, avg time-to-ticket, % escalated  
- [ ] 3-minute demo script + 5-slide deck  
- [ ] README + architecture diagram  
- [ ] Deploy (Vercel frontend + any cloud/API backend)  

---

## Demo script (3 minutes)

1. **Problem (20s):** Aid requests are messy; wrong routing; duplicates.  
2. **Live (90s):** Type: “Flood ke baad khane ki zaroorat hai, Township Lahore, family of 5.”  
   Show agents running → triage Food → match resource → ticket created.  
3. **Integrity (30s):** Same phone again → duplicate flagged.  
4. **Critical (30s):** “Chest pain, need ambulance” → escalate to Supervisor → Approve.  
5. **Close (20s):** Dashboard metrics + Alibaba Cloud architecture.  

---

## Sample seed data ideas

- Food packs: Alkhidmat Lahore Kitchen, stock 120  
- Shelter: Temporary camp Johar Town, capacity 40 families  
- Blood: Sundas Foundation / mock blood bank O+ available  
- Volunteers: 8 names with phone + skill tags  

---

## Repo / naming

- Repo: `alkhidmat-relief-copilot`  
- Title on GitHub: Alkhidmat Relief Copilot — Agentic AI Aid Desk  

---

## What NOT to do

- Don’t build 10 agents — 4–6 max, rock solid  
- Don’t depend on real NGO login in v1  
- Don’t skip Urdu sample  
- Don’t skip HITL — judges love “safe agents”  

---

## Next action for you

1. Register with the Short Detail above before Aug 7  
2. Tell me when registration is done  
3. Say **“start build”** and we scaffold the FastAPI + LangGraph repo in this workspace  
