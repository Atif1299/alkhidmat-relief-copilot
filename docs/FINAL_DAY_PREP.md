# National Final Prep — 24 Oct 2026, Islamabad

Project P00627 · Muhammad Atif · Abdul Ahad

**Order to present:** one medical case and its end result → how the agents get there → business model → the pilot ask.
Say "working prototype, ready for a pilot". Never say "demo project".

---

## Part 1 — Deck changes (in `alkhidmat_relief_copilot_final.pptx`)

| Slide | Change |
|-------|--------|
| 4 · Architecture | Integrity now reads "Same phone within 48h; critical or high-risk → supervisor" (no CNIC claim). Knowledge reads "Category-filtered SOPs · pgvector + keyword fallback". |
| 8 · Impact | "~23s — Live average, request to ticket", the production dashboard figure for cases the agents dispatched on their own. |
| 9 · Cloud | Cloud Run row adds "portable to Alibaba ECS / SAE". The footer no longer overlaps the last row. |
| 10 · **Business model (new)** | "NGOs Pay, Requesters Never Do": Who pays · How they pay · Why it pays back. Speaker notes below are in the slide notes. |
| 12 · Close | "Our ask" card: one Alkhidmat district office for a 3-month pilot. |

Business model in one line each, if a judge digs in:

| Block | What to say |
|-------|-----------|
| **Who pays** | Relief NGOs and their regional offices. Requesters never pay. Small NGOs get licences funded by donors or company CSR. |
| **How they pay** | Yearly subscription per organisation, priced by case volume and number of branches, plus a one-time setup to load the NGO's SOPs and connect its volunteer roster or CRM. |
| **Why NGOs pay** | Duplicate claims stop draining stock · desk hours saved on routing · an audit trail for every decision, ready for donor reporting. |
| **White-label** | Each NGO gets its own workspace, categories, SOPs, resources and volunteers. Same agents, same supervisor gate. |

**Speaker notes for slide 10 (about 30 s):**
> "Our customer is the NGO, not the citizen. Requesters never pay. NGOs pay a yearly subscription based on how many cases and branches they run, plus a one-time setup to load their own SOPs and connect their volunteer system. For small NGOs, donors or company CSR can fund the licence. Why they'd pay: fewer duplicate claims eating their stock, less desk time on routing, and an audit trail they can show donors. We want to start with a free pilot at one Alkhidmat district office, measure the savings, and set the price on those numbers."

---

## Part 2 — Judge Q&A (short answers, say them in your own words)

**1. "Take a medical case. What's the end result?"**
Example: "Chest pain, need ambulance, Johar Town." Triage marks it Medical, Critical, and the citizen gets an AKD ticket number immediately. Integrity sends it to a supervisor, who approves with one click. The Matcher assigns the Alkhidmat Mobile Clinic in Johar Town and the volunteer Fatima Ali (medical, same area). The citizen sees "dispatched" with the clinic and volunteer names on /status. The desk gets the full timeline and a PDF.
*"We don't send the ambulance. We get the NGO's nearest medical team a checked, prioritised case with a named person on it within a minute."*

**2. "Why make a chest-pain patient wait for a supervisor?"**
The supervisor step doesn't control emergency care. It controls when the NGO commits its limited resources. Life-threatening cases should go to Rescue 1122 first, and the request page already shows the citizen a "call Rescue 1122 now" prompt (in English and Urdu) the moment a case is marked critical medical, before any approval.

**3. "Can it handle other kinds of aid?"**
Yes. A new aid type is data, not new code: add the category, an SOP document, and that NGO's resources and volunteers. The agents, Integrity check, supervisor step and dashboard stay the same. We built for six categories (Food, Medical, Shelter, Blood, Education, Other) because those are Alkhidmat's main programmes.

**4. "How does it scale?"**
The app runs in stateless containers on Cloud Run, so more traffic means more containers. Cases, approvals and the agents' saved progress live in Postgres. Each NGO is a separate workspace. A paused case survives a server restart because the pipeline's state is saved.

**5. "Why Google Cloud at an Alibaba hackathon?"**
The AI (Qwen and embeddings) runs on Alibaba DashScope. The Alibaba ECS free trial wasn't available to us, so we hosted the containers on Cloud Run. They're standard Docker images, so moving to Alibaba ECS or Serverless App Engine is a deploy step, not a rewrite.

**6. "Where exactly is Qwen used?"**
Intake (reading Urdu or English, pulling out need, location, phone and name) and Triage (category and priority). The Knowledge step is built for DashScope embeddings with pgvector; on the live site it is currently running on its keyword fallback, because the API key doesn't have embeddings access yet. Integrity, Matcher and Dispatch are deterministic code, on purpose: decisions about money and resources should be rules you can audit.

**7. "What if the AI gets it wrong?"**
Qwen only picks from fixed categories and priorities, at low temperature. Phone numbers and locations are also pulled out by rules and merged in. Every critical or risky case goes to a human. Every agent step is logged in the trace, so a wrong call is visible and can be corrected.

**8. "How do you catch fraud and duplicates?"**
Today: the same phone number within 48 hours goes to a supervisor, along with every critical case. Missing phone raises the risk score. Next: CNIC and household matching once an NGO connects its beneficiary records. *(Don't claim a CNIC check. There isn't one yet.)*

**9. "Why many agents instead of one prompt?"**
Each step has one job, its own log, and can be tested on its own. The Integrity check can't be skipped, because it's part of the graph's structure, not a prompt instruction. The graph can pause for a human and resume later from where it stopped. One big prompt can't guarantee any of that.

**10. "What about citizens' privacy?"**
Citizens don't need an account. Checking status needs the ticket number plus the same phone number, and a wrong pair gets a generic "not found". The citizen view never shows risk scores, the agent trace, supervisor notes or volunteer phone numbers. Staff pages need a login with a role (desk or supervisor).

**11. "Is this real data? What's live and what's not?"**
The app, agents, supervisor step, status page and dashboard are live on the public URL. The Lahore resources and volunteers are sample data we created. SMS/WhatsApp notifications are not connected yet: the citizen checks /status instead. Real inventory and CRM connections come with the pilot.

**12. "Who's the competition? Why not a CRM?"**
CRMs store cases after a person has read and sorted them. We do the reading, sorting, checking and matching before a case reaches the CRM, in Urdu and English, and we can push the result into the NGO's existing CRM.

**13. "What do you need next?"**
One Alkhidmat district office for a 3-month pilot, with real intake, so we can measure time-to-ticket, duplicate claims caught, and desk hours saved.

**14. "Are these Alkhidmat's real SOPs?"**
No. They are 18 sample SOPs we wrote for the prototype: three per aid line (food, medical, shelter, blood, education) plus duplicate, escalation and Urdu-phrase guides. Each case cites only its own category's SOPs, and Integrity cites the rule that sent a case to a supervisor. In the pilot, Alkhidmat loads its own SOPs and the desk reindexes them automatically.

**15. "What does ~23 seconds measure?"**
The live dashboard's average from request to ticket for cases the agents dispatched on their own. Cases that wait for a supervisor are counted separately, because that wait is a person's decision, not desk processing.

---

**Before your slot:** open the live site and submit one request. The API keeps one instance warm, so it should answer quickly. `AKD-SEED-006` is now dispatched: use the "Waiting · medical" chip on /status to show the end result (clinic and volunteer). For the waiting state, submit a fresh chest-pain request live and approve it in front of the judges. Type a fresh phone number for the food example so it isn't flagged as a duplicate.
