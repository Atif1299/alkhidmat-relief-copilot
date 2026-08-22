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

### 2026-08-23 — Product identity: NGO Aid Desk SaaS (not chatbot)

**Context:** User only submitted short registration blurb; asked if product is SaaS, simple copilot, and what enhancements win vs ~2900. Training slides: real problem, thin prototype, impact visible, not most complicated.  
**Decision:** Position as **agentic relief ops desk (B2B/NGO SaaS module)** — multi-agent ticket workflow + HITL + metrics. Enhancements allowed within Tier A/B in `docs/PRODUCT_DEFINITION.md`. Reject Tier C mega-scope. Light RAG only after Tier A.  
**Alternatives considered:** Consumer chatbot; full commercial SaaS with billing/WhatsApp; architecture rewrite to unrelated domain.  
**Judge impact:** Matches Alkhidmat host + “industry usable” + slide winning signal (user knows next action).  
**Status:** accepted

### 2026-08-23 — .cursor synced to Tier A architecture + repo

**Context:** Pre-implementation; user created GitHub repo and asked .cursor to match PRODUCT_DEFINITION tiers.  
**Decision:** Updated `.cursor/rules/` and `.cursor/skills/` with LangGraph stack, Tier A/B order, repo URL, git push-per-todo, Next.js 14. Commit `.cursor/` to repo.  
**Status:** accepted
