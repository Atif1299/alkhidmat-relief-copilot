# Hackathon Master Plan — Alkhidmat Relief Copilot

**Event:** Alibaba Cloud AI Hackathon Pakistan 2026  
**Theme:** AI for Pakistan's Future  
**Host:** Alkhidmat Foundation Pakistan / Bano Qabil Platform  
**Qualification:** **Grade 1** (met every threshold at first assessment)  
**Tools:** Qoder Enterprise Plan + special Credits (after acknowledgement)  
**Status:** Build phase extended — **to 4 September 2026**

---

## Official timeline (UPDATED 23 Aug)

| Phase | Dates | Notes |
|-------|-------|-------|
| Training | 19–20 Aug | Required; attendance verified before Qoder licence |
| Acknowledgement | **By 24 Aug 17:00 PKT** | Form required before Qoder dispatch |
| Qoder dispatch | **24–25 Aug** | After acknowledgement |
| **Build** | **Until 4 September** | Online |
| Submission portal | During build | Details TBA |
| Regional technical evaluation | **After 4 Sep** | Dates/venues TBA |
| Grand Finale | 10 Sep (was fixed earlier) | Confirm if still valid when organizers update |

**Superseded:** Old build end 27 Aug and regional 28–30 Aug — no longer the plan.

**Official channels:** aihackathon@banoqabil.pk + Discord

---

## Cursor chat sessions (workflow)

User splits work across chats; **this mentor thread** is the master hub.

| Session purpose | Use for |
|-----------------|---------|
| **This chat (Hackathon project mentor)** | Organizer emails, accounts, scope, Tier order, submission, demo, pitch — **source of truth for hackathon decisions** |
| Idea enhancements | Product definition, Tier scope, architecture choices |
| Tier 1 implementation | Code scaffold, agents, API, UI |
| Tier 1 requirements fulfillment | Gap fixes, DashScope, tests, polish |
| Tier 2+ (later) | Only after Tier A E2E green |

**Rule:** Decisions from side chats must land in `docs/DECISIONS.md`, `docs/EMAIL_LOG.md`, or `docs/PRODUCT_DEFINITION.md` so this hub stays synced. Return here before submission packaging.

---

## Win thesis

| Pillar | Our angle |
|--------|-----------|
| **Grade 1 already earned** | Idea + qualification strong — win now on **technical implementation** |
| **Mission fit** | Alkhidmat relief ops desk |
| **Agentic AI** | LangGraph + specialist agents + HITL |
| **Alibaba toolchain** | Qoder Enterprise + Qwen |
| **Localization** | Urdu + English |
| **Regional focus** | Technical strength, not just pitch |

---

## Build plan (to 4 Sep)

Use time for a solid Tier A MVP, then polish — do not invent scope.

| Window | Focus |
|--------|--------|
| Now – 25 Aug | Acknowledge form; Qoder arrives; scaffold + English E2E |
| 26 Aug – 31 Aug | HITL, Urdu, duplicate/critical paths, agent trace |
| 1–3 Sep | Dashboard, **GCP Cloud Run deploy**, demo rehearsal |

**Deploy decision (27 Aug):** Alibaba ECS free trial blocked → live app on **GCP `x-saas` Cloud Run**; LLM remains **DashScope**. See `docs/DEPLOYMENT.md`.
| 4 Sep | Submission portal (when shared) |

---

## MVP scope (Tier A)

### Must ship

- [ ] Web chat UI  
- [ ] LangGraph: Intake → Triage → Integrity → Matcher → Dispatch  
- [ ] HITL supervisor  
- [ ] DB + Lahore seed data  
- [ ] Dashboard metrics  
- [ ] Urdu + English demo paths  
- [ ] Qwen via Alibaba stack  
- [ ] Build/demo story on Qoder Enterprise  

### Defer unless rubric demands

- [ ] Heavy Agentic RAG  
- [ ] WhatsApp production  
- [ ] Real Alkhidmat API  

---

## Immediate action checklist (you)

- [ ] **TODAY: Form by 17:00 PKT** — https://forms.gle/rxdWSej496y7HtT5A  
- [ ] Confirm both training attendance forms were submitted  
- [ ] Do **not** create Qoder account on `ranaatif1299@gmail.com`  
- [ ] Watch inbox 24–25 Aug for licence  
- [ ] Say **"start build"** when ready to code  

---

## Document index

| File | Purpose |
|------|---------|
| `Alkhidmat_Relief_Copilot.md` | Original brief |
| `docs/EMAIL_LOG.md` | Organizer emails |
| `docs/EVALUATION_CRITERIA.md` | Rubric mapping |
| `docs/ACCOUNTS_AND_PLATFORMS.md` | Accounts / Qoder |
| `docs/DECISIONS.md` | Mentor decisions |
| `AGENTS.md` | Product + workflow agents |
