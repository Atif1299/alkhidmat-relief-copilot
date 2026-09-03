---
name: Citizen status lookup
overview: "Add a public “check my request” path: every intake gets an AKD number immediately, and a citizen looks it up later with that number plus the phone they gave — no account, no staff APIs, aligned with guest intake and HITL."
todos:
  - id: mint-ticket-intake
    content: Mint AKD ticket_id on every new case (including HITL/processing); show it on /request HITL outcome
    status: completed
  - id: public-status-api
    content: Guest POST /api/v1/public/status with ticket+phone; citizen DTO + 404 on mismatch; tests
    status: completed
  - id: status-page-nav
    content: Public /status page, PUBLIC_PATHS, chrome + landing entry, request outcome link
    status: completed
  - id: docs-demo
    content: Demo script + architecture public-route note for status check
    status: completed
isProject: false
---

# Citizen request status (public track)

You are right: today the winning signal (“know what happens next”) only exists **on the submit screen**. If the citizen leaves, there is no way back. Staff have tickets/timeline; guests do not.

This is not a new agent. It is a **public surface on the existing case**, in the same IA as Request aid.

## How the product works today

```mermaid
flowchart LR
  guest["Guest /request"] --> graph["LangGraph pipeline"]
  graph -->|"clear"| dispatch["Dispatch stamps AKD ticket"]
  graph -->|"critical or duplicate"| hitl["pending_hitl — often no ticket_id"]
  hitl -->|"supervisor approve"| dispatch
  dispatch --> staff["Staff /tickets /cases"]
  guest -.->|nothing| statusGap["No return path"]
```

- Citizens **must not log in** ([docs/PRODUCT_DEFINITION.md](docs/PRODUCT_DEFINITION.md), [frontend/lib/roles.ts](frontend/lib/roles.ts) public paths: `/`, `/request`, `/login`).
- Role `requester` is a seeded JWT for API tests, not a citizen portal.
- [backend/app/tools/cases.py](backend/app/tools/cases.py) mints `AKD-YYYYMMDD-XXXXXX` only when status is `open` / `dispatched`. HITL rows often have **no ticket** — the request page even says you get a ticket after approval.
- [backend/app/api/cases.py](backend/app/api/cases.py) `GET /cases/{id}` is JWT (`RequireRequester` / desk). Guests cannot call it.
- Duplicate detection is **phone digits in 48h** (`search_similar_cases`). Phone is the real-world identity; the AKD number is the receipt.
- `send_status_message` is already a **stub notify** (audit log only). WhatsApp stays deferred. Status check is the honest channel until SMS exists.

## Locked design (fits architecture)

**No citizen accounts.** No phone-only inbox (anyone who knows a mobile number would see every request).

**Track with: AKD number + the same phone used on the request.** Same pattern as a courier slip. Wrong pair returns a generic “not found” (do not leak that the ticket exists).

**Mint the AKD number at intake**, not only at Dispatch. Dispatch still means “verified and matched”; the number is the **receipt from the first moment**, including HITL. Otherwise a critical medical request has nothing to check.

Citizen-facing stages (reuse [backend/app/services/timeline.py](backend/app/services/timeline.py), strip staff-only detail):

| Status | What they see |
|--------|----------------|
| `processing` | Received — desk is running |
| `pending_hitl` | Waiting for supervisor |
| `dispatched` | Ticket dispatched — resource + volunteer name |
| `rejected` | Not approved — no internal HITL note |
| `closed` | Closed |

Public payload **must not** include: full agent trace, SOP bodies, risk score, other cases, supervisor notes, volunteer personal phone (name + kitchen is enough).

**Do not reuse** `GET /api/v1/cases/{id}`. It is JWT-gated but has **no owner filter** and returns `serialize_case` (raw message, phone, trace). The public route is a new thin DTO. Same 404 for unknown ticket and wrong phone so existence is not leaked. Never wrap Integrity `search_similar_cases` (phone is the duplicate key; demo chip `03001234567` would dump every case on that number).

## Implementation

### 1. Always issue the receipt

In [backend/app/tools/cases.py](backend/app/tools/cases.py) `create_case` / `ensure_draft_case`: mint `ticket_id` for every new row (`processing` and `pending_hitl` too). Dispatch in [backend/app/agents/nodes.py](backend/app/agents/nodes.py) keeps the existing ID if present.

Update [frontend/app/request/page.tsx](frontend/app/request/page.tsx) HITL banner to show the stamp: “Your request number is `AKD-…`. Check status anytime.” Link to `/status?ticket=`.

### 2. Public status API

New guest route (same guest pattern as chat: [backend/app/deps/auth.py](backend/app/deps/auth.py) `OptionalChatUser` / no JWT):

`POST /api/v1/public/status` `{ ticket_id, phone }`

- Normalize ticket (`trim`, upper-case) and phone (digits only).
- Lookup `cases.ticket_id`; compare phone digits to `requester_phone`.
- Mismatch or missing → **404** `"Request not found"`.
- Success: ticket, status, category, next-action copy, **citizen timeline** (skip skipped HITL if not required), optional resource name + volunteer **name** if dispatched.

Do not reuse `serialize_case`. Add a pytest: guest 200 with matching phone; 404 with wrong phone; supervisor queue still 401 without JWT.

### 3. Public `/status` page

- New [frontend/app/status/page.tsx](frontend/app/status/page.tsx): ticket + phone fields, sitrep card + existing [frontend/components/CaseTimeline.tsx](frontend/components/CaseTimeline.tsx).
- Add `/status` to `PUBLIC_PATHS` in [frontend/lib/roles.ts](frontend/lib/roles.ts).
- Public nav in [frontend/components/AppChrome.tsx](frontend/components/AppChrome.tsx): **Check status** beside Request aid.
- Landing door in [frontend/app/page.tsx](frontend/app/page.tsx).
- Demo chips: e.g. seed `AKD-SEED-001` + known seed phone so the path works without a live submit.

### 4. Docs / demo (one beat)

[docs/DEMO_SCRIPT.md](docs/DEMO_SCRIPT.md): after food ticket, open **Check status**, paste AKD + phone, show dispatched vs a HITL ticket still waiting. [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) public routes table.

## Out of scope

- SMS / WhatsApp (keep `send_status_message` stub)
- Citizen JWT / `requester` portal
- Phone-only list of all requests
- New LangGraph agents
- Changing staff tickets IA

## Demo after this

Citizen submits → number on screen → leaves → **Check status** with AKD + phone → sees waiting / dispatched / next action. Same desk, closed loop.
