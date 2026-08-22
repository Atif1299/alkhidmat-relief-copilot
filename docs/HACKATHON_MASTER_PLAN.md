# Hackathon Master Plan — Alkhidmat Relief Copilot

**Event:** Alibaba Cloud AI Hackathon Pakistan 2026  
**Theme:** AI for Pakistan's Future  
**Host:** Alkhidmat Foundation Pakistan / Bano Qabil Platform  
**Selection:** ~2,900 / ~16,000  
**Status:** **Build phase — 22–27 Aug 2026** (Day 1 = today)

---

## Official timeline (from emails)

| Phase | Dates | Mode | Notes |
|-------|-------|------|-------|
| Training | 19–20 Aug | Online, required | Qoder Quest + Qoder IDE |
| Qoder access | 21 Aug | Email to participation address | Do not self-register that email before 21 Aug |
| **Build** | **22–27 Aug** | Online | Core product week |
| Regional | 28–30 Aug | In person | Karachi, Lahore, Islamabad — date TBA |
| Judging | 31 Aug – 2 Sep | — | Finalist selection |
| Finalist prep | 3–9 Sep | — | Polish for finale |
| Grand Finale | 10 Sep | In person | National |

**User location:** Lahore — regional round likely local (venue TBA).

**Official channels:** aihackathon@banoqabil.pk + Discord https://discord.gg/xfyUK45Ka

---

## Win thesis (updated)

| Pillar | Our angle | Email signal |
|--------|-----------|--------------|
| **Mission fit** | Alkhidmat relief workflow | Hosted by Alkhidmat; theme AI for Pakistan |
| **Agentic AI** | Multi-agent orchestration + HITL | Training: LLMs, live building |
| **Alibaba toolchain** | Qoder + DashScope/Qwen | Qoder access provided; Skills/MCP in training |
| **Localization** | Urdu + English | Pakistan-first theme |
| **Live demo** | 3-min regional presentation | Regional rounds in person |
| **Social impact** | Measurable aid routing | Selection standards favored real problems |

---

## Build week plan (22–27 Aug)

### 22 Aug (Day 1) — Core backend + agents
- M1: FastAPI + DB + seed data  
- M2: LangGraph — Intake, Triage, Integrity, Dispatch (English E2E)

### 23 Aug (Day 2) — UI + matcher
- M3: Chat UI + ticket list  
- Resource Matcher agent + mock inventory

### 24 Aug (Day 3) — Safety + Urdu
- M4: HITL supervisor screen  
- Urdu prompts + duplicate + critical paths

### 25 Aug (Day 4) — Cloud + visibility
- DashScope/Qwen integration  
- Agent trace in UI  
- OSS stub (optional upload)

### 26 Aug (Day 5) — Dashboard + deploy
- Metrics dashboard  
- Deploy API + frontend  
- README + architecture diagram

### 27 Aug (Day 6) — Submission prep buffer
- Demo rehearsal (3 min)  
- Deck draft  
- **Wait for official submission format email** before final packaging

---

## MVP scope (unchanged — optimized for 6-day build)

### Must ship by 27 Aug

- [ ] Web chat UI  
- [ ] LangGraph: Intake → Triage → Integrity → Matcher → Dispatch  
- [ ] HITL supervisor  
- [ ] DB + Lahore seed data  
- [ ] Dashboard metrics  
- [ ] Urdu + English demo paths  
- [ ] Qwen/DashScope (Alibaba Cloud LLM)  
- [ ] Qoder story in README (provided toolchain)

### Should ship (25–26 Aug)

- [ ] Agent trace visible in UI  
- [ ] Architecture diagram with Alibaba Cloud services  

### Defer unless submission email demands

- [ ] Agentic RAG  
- [ ] WhatsApp integration  
- [ ] Real Alkhidmat API  

---

## Demo script (3 min — regional round)

1. **Problem (20s)** — Aid chaos, wrong routing, duplicates  
2. **Live (90s)** — Urdu flood/food request → agents → ticket  
3. **Integrity (30s)** — Same phone → duplicate flagged  
4. **Critical (30s)** — Chest pain → Supervisor approves  
5. **Close (20s)** — Dashboard + Alibaba Cloud / Qoder architecture  

---

## Open questions (fill from next emails)

| # | Question | Source | Answer |
|---|----------|--------|--------|
| 1 | Official evaluation rubric / weights? | TBD | |
| 2 | Required Alibaba Cloud products? | Partial: Qoder confirmed | |
| 3 | Submission format (video, repo, deck)? | TBD — during build phase | |
| 4 | Submission deadline? | TBD | |
| 5 | Lahore regional — exact date + venue? | TBD | |
| 6 | Prize categories? | TBD | |
| 7 | Contents of attached Programme Schedule? | Email 3 attachment | User to share |

---

## Immediate action checklist (you)

- [ ] Join Discord: https://discord.gg/xfyUK45Ka  
- [ ] Set Discord name: **Muhammad Atif — Alkhidmat Relief Copilot — Multi-Agent Aid Desk**  
- [ ] Read Discord code of conduct  
- [ ] Submit training attendance forms (19 Aug + 20 Aug) if not done — use ranaatif1299@gmail.com  
- [ ] Watch **Session 2 recording** (Skills/MCP): https://resource.alibabacloud.com/activity/webinar/detail.html?id=LS20260010  
- [ ] Check inbox/spam for **Qoder access** email (expected 21 Aug — may be separate from recording notice)  
- [ ] Share PDF: *Training and Programme Schedule* attachment (may contain rubric)  
- [ ] Share remaining 2 emails when ready  
- [ ] Say **"start build"** when ready to scaffold code

---

## Document index

| File | Purpose |
|------|---------|
| `Alkhidmat_Relief_Copilot.md` | Original hackathon brief |
| `docs/EMAIL_LOG.md` | Organizer communications |
| `docs/EVALUATION_CRITERIA.md` | Rubric → feature mapping |
| `docs/DECISIONS.md` | Mentor decision log |
| `docs/ACCOUNTS_AND_PLATFORMS.md` | Accounts, Qoder rules, platform decisions |
