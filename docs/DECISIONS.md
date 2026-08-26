# Mentor Decision Log

---

## Decisions

### 2026-08-22 — Foundation-first, emails before build

**Context:** Selected from ~16k apps; full rubric not yet ingested.  
**Decision:** Phase 0 = skills, agents, plans; implementation on "start build".  
**Status:** accepted → **superseded by build phase start 22 Aug**

### 2026-08-22 — MVP without RAG by default

**Context:** User asked about Agentic RAG / ecosystem.  
**Decision:** Ship 4–6 orchestrated agents first; RAG only if rubric demands.  
**Status:** accepted

### 2026-08-22 — Compress plan to 6-day build window

**Context:** Email 2–3 confirm build phase 22–27 Aug (not 48h weekend).  
**Decision:** Spread milestones across 6 days; use 27 Aug as submission-prep buffer pending official format email.  
**Judge impact:** More polish time for regional demo; less panic scope.  
**Status:** accepted

### 2026-08-22 — Qoder as official toolchain (not optional)

**Context:** Email 3 — Qoder access issued 21 Aug; training on Qoder Quest + IDE with Skills/MCP.  
**Decision:** Document Qoder in architecture; use participation-email Qoder account; do not fight the toolchain. LLM via DashScope/Qwen inside or alongside Qoder story.  
**Alternatives considered:** Ignore Qoder, build only in Cursor.  
**Judge impact:** Aligns with sponsor-provided stack — likely scored.  
**Status:** accepted

### 2026-08-22 — Wait for official submission format

**Context:** Email 3 explicitly says submission details come during build phase; ignore unofficial formats.  
**Decision:** Build working product + demo; defer final packaging until organizer email.  
**Status:** accepted

### 2026-08-22 — Qoder access delayed; parallel build track

**Context:** Build Day 1 (22 Aug). No Qoder provisioning email; only unrelated Alibaba Cloud sales outreach (`@alibaba-inc.com`).  
**Decision:** Contact `aihackathon@banoqabil.pk` + Discord; scaffold in Cursor/repo now; port to Qoder when access arrives. Do not self-register participation email on Qoder.  
**Status:** accepted

### 2026-08-24 — Timeline extended; Grade 1; acknowledge for Qoder Enterprise

**Context:** Emails 9–10. Build to 4 Sep. User is Grade 1 → Qoder Enterprise + special Credits after form by 24 Aug 17:00 PKT. Regional = technical evaluation after 4 Sep.  
**Decision:** Complete acknowledgement immediately. Do not self-register Qoder. Use extra time for Tier A quality, not Tier C features. Regional win path = technical implementation strength.  
**Status:** accepted

### 2026-08-26 — Qoder Repo Wiki: optional map of code; not plan source of truth

**Context:** `.qoder/repowiki` generated (~100 files). Overview/agents largely match repo. Some pages invent scope (e.g. AWS ECS deployment) vs our Alibaba/hackathon plan.  
**Decision:** Primary build stays Cursor using `docs/PRODUCT_DEFINITION.md`, `HACKATHON_MASTER_PLAN.md`, `DECISIONS.md`. Wiki = optional codebase map — `@` specific pages when exploring code. Ignore cloud/deploy pages that contradict Alibaba stack. Do not regenerate wiki for credits. Do not treat wiki as Tier A/B roadmap.  
**Status:** accepted

### 2026-08-26 — Build primary in Cursor; Qoder optional for credits/story

**Context:** User joined Pakistan Hackathon Program on Qoder (2490 credits). Repo Wiki auto-gen burned ~34 credits; user prefers Cursor and doesn't want to learn full Qoder IDE. Emails: tooling supports work, does not determine regional outcome (technical implementation does).  
**Decision:** Primary build stays in **Cursor**. Keep Qoder account/org active. Optional light Qoder use for Skills/MCP demos or judge screenshots. Cancel/pause wasteful Repo Wiki regen. Document Qoder + DashScope in architecture. Do not force daily Qoder-only workflow.  
**Status:** accepted

### 2026-08-26 — Qoder: install IDE only; accept Teams invite with registered email

**Context:** Invite to org "Pakistan Hackathon Program"; code 235521; expires 27 Aug 11:20 UTC. Download page shows IDE, JetBrains, CLI, Mobile, Wake, Work.  
**Decision:** Accept invite with `ranaatif1299@gmail.com`. Download **Qoder IDE — Windows X64 (User)**. Skip JetBrains/CLI/Mobile/Wake/Work unless later needed. Keep Cursor for mentor hub; use Qoder for hackathon build credits/Skills/MCP story.  
**Status:** accepted

### 2026-08-24 — Multi-session Cursor workflow

**Context:** User runs separate chats for idea enhancement, Tier 1 build, Tier 1 requirements, future Tier 2; this thread is master mentor hub for emails + submission.  
**Decision:** This chat owns hackathon context, organizer mail, submission, demo/pitch. Build chats implement; log outcomes to `docs/` so hub stays current.  
**Status:** accepted


**Context:** User only submitted short registration blurb; asked if product is SaaS, simple copilot, and what enhancements win vs ~2900. Training slides: real problem, thin prototype, impact visible, not most complicated.  
**Decision:** Position as **agentic relief ops desk (B2B/NGO SaaS module)** — multi-agent ticket workflow + HITL + metrics. Enhancements allowed within Tier A/B in `docs/PRODUCT_DEFINITION.md`. Reject Tier C mega-scope. Light RAG only after Tier A.  
**Alternatives considered:** Consumer chatbot; full commercial SaaS with billing/WhatsApp; architecture rewrite to unrelated domain.  
**Judge impact:** Matches Alkhidmat host + “industry usable” + slide winning signal (user knows next action).  
**Status:** accepted

### 2026-08-23 — .cursor synced to Tier A architecture + repo

**Context:** Pre-implementation; user created GitHub repo and asked .cursor to match PRODUCT_DEFINITION tiers.  
**Decision:** Updated `.cursor/rules/` and `.cursor/skills/` with LangGraph stack, Tier A/B order, repo URL, git push-per-todo, Next.js 14. Commit `.cursor/` to repo.  
**Status:** accepted

### 2026-08-26 — Tier B architecture locked (B8–B12)

**Context:** Tier A E2E green; separate chat for Tier 2 implementation.  
**Decision:** Extend graph with Knowledge node after Triage (file SOPs + keyword `sop_chunks`, no vector DB). Demo role switcher (no JWT). Timeline API + case detail page. Expand Lahore seed. Server PDF via reportlab. Integrity and HITL path unchanged.  
**Alternatives considered:** Hermes; full embeddings/vector DB; real OAuth roles.  
**Judge impact:** Visible SOPs + ops timeline + PDF = industry-usable Aid Desk, not chatbot.  
**Status:** accepted
