import Link from "next/link";
import { SitrepReplay } from "@/components/SitrepReplay";
import { StackStrip } from "@/components/StackStrip";

const AID_LINES = [
  { en: "Food", ur: "خوراک" },
  { en: "Medical", ur: "طبی امداد" },
  { en: "Shelter", ur: "پناہ" },
  { en: "Blood", ur: "خون" },
  { en: "Education", ur: "تعلیم" },
];

const TODAY = [
  "Requests land in WhatsApp, calls and paper forms",
  "Staff read every message to work out the need and the area",
  "The same family asks twice and nobody notices",
  "A chest-pain case waits behind routine food requests",
  "The requester has no number to follow up with",
];

const WITH_DESK = [
  "One intake in Urdu or English, structured in seconds",
  "Category and priority set by Triage, checked against SOPs",
  "Repeat requests from the same phone go to a supervisor",
  "Critical medical cases jump to a human, with a 1122 prompt",
  "Every requester leaves with an AKD number to track",
];

const STEPS = [
  { n: "01", title: "Request", body: "A citizen writes the need in Urdu or English. No account, no app." },
  { n: "02", title: "Verify", body: "Agents extract the details, classify, read the SOP and run the Integrity check." },
  { n: "03", title: "Match", body: "Nearest stock and a volunteer with the right skills in the same area." },
  { n: "04", title: "Track", body: "An AKD number plus the same phone shows status at any time." },
];

const INPUTS = [
  { k: "The request", v: "Urdu · Roman Urdu · English" },
  { k: "Your SOPs", v: "Food · medical · shelter rules" },
  { k: "Your resources", v: "Kitchens · clinics · camps · blood banks" },
  { k: "Your volunteers", v: "Skills and areas" },
];

const AGENTS = ["Intake", "Triage", "Knowledge", "Integrity", "Matcher", "Dispatch"];

const OUTCOMES = [
  { k: "AKD ticket", v: "Issued on every request" },
  { k: "Matched resource", v: "Name, area and contact" },
  { k: "Named volunteer", v: "Same area, right skills" },
  { k: "Audit trail", v: "Timeline · agent trace · PDF" },
];

const RULES = [
  {
    when: "Critical medical",
    then: "Pauses for a supervisor. The requester sees a Rescue 1122 prompt straight away.",
  },
  {
    when: "Same phone within 48h",
    then: "Flagged as a possible duplicate. A person decides; nobody is auto-rejected.",
  },
  {
    when: "Every decision",
    then: "Who approved, when and why is logged on the case timeline and in the PDF.",
  },
];

const NUMBERS = [
  { value: "6", label: "specialised agents in one governed pipeline" },
  { value: "2", label: "languages at intake, Urdu and English" },
  { value: "7", label: "SOP documents the Knowledge agent cites" },
  { value: "27", label: "Lahore relief resources in the prototype dataset" },
  { value: "17", label: "volunteers matched by skill and area" },
  { value: "26", label: "automated tests, including duplicate and escalation paths" },
];

const NGO_POINTS = [
  { k: "Your categories", v: "Add an aid line as data, not new code." },
  { k: "Your knowledge", v: "Load your SOPs; agents cite them on every case." },
  { k: "Your people", v: "Connect your volunteer roster or CRM." },
  { k: "Your brand", v: "One workspace per NGO, under your name." },
];

export default function HomePage() {
  return (
    <div className="landing">
      <section className="sitrep-hero">
        <div className="landing-hero">
          <p className="eyebrow">Alkhidmat-style relief operations</p>
          <h1>
            From a messy aid request to a verified ticket
            <span className="hero-accent"> — with a human when it matters</span>
          </h1>
          <p className="urdu hero-urdu" lang="ur">
            اردو یا انگریزی میں درخواست دیں — ٹکٹ یا سپروائزر تک پہنچیں
          </p>
          <p className="landing-lede">
            Submit in Urdu or English. Six agents verify, check the SOP, catch duplicates and match
            stock. You leave with a request number you can check later, or a supervisor hold.
            Never a silent queue.
          </p>
          <div className="landing-ctas">
            <Link className="btn btn-lg" href="/request">
              Request aid
            </Link>
            <Link className="btn secondary btn-lg" href="/status">
              Check status
            </Link>
          </div>
          <ul className="hero-proof" aria-label="What to expect">
            <li>No account needed</li>
            <li>Urdu or English</li>
            <li>Supervisor approval on critical cases</li>
          </ul>
        </div>
        <SitrepReplay />
      </section>

      <section className="aid-lines" aria-labelledby="aid-lines-heading">
        <p id="aid-lines-heading" className="eyebrow l-eyebrow">
          One desk for every relief line
        </p>
        <ul>
          {AID_LINES.map((line) => (
            <li key={line.en}>
              <span>{line.en}</span>
              <span className="urdu" lang="ur">
                {line.ur}
              </span>
            </li>
          ))}
        </ul>
      </section>

      <section className="l-section" aria-labelledby="why-heading">
        <header className="l-head">
          <p className="eyebrow l-eyebrow">Why it matters</p>
          <h2 id="why-heading">Requests arrive messy. Critical cases get buried.</h2>
          <p className="muted">
            The first minute after a request arrives decides how fast help moves. Today that minute
            is spent reading, sorting and guessing.
          </p>
        </header>
        <div className="compare">
          <div className="compare-col compare-before">
            <p className="compare-label">Today · manual desk</p>
            <ul>
              {TODAY.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </div>
          <div className="compare-col compare-after">
            <p className="compare-label">With the Aid Desk</p>
            <ul>
              {WITH_DESK.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </div>
        </div>
      </section>

      <section className="l-section" aria-labelledby="how-heading">
        <header className="l-head">
          <p className="eyebrow l-eyebrow">How it works</p>
          <h2 id="how-heading">From request to resolved, in four steps.</h2>
        </header>
        <ol className="flow-steps">
          {STEPS.map((step) => (
            <li key={step.n}>
              <span className="flow-num">{step.n}</span>
              <strong>{step.title}</strong>
              <p className="muted">{step.body}</p>
            </li>
          ))}
        </ol>
      </section>

      <section className="l-section" aria-labelledby="engine-heading">
        <header className="l-head">
          <p className="eyebrow l-eyebrow">The desk</p>
          <h2 id="engine-heading">One pipeline between a request and the field team.</h2>
          <p className="muted">
            The NGO brings its rules, stock and people. The desk reads, checks and matches, then
            hands back a ticket with a full record of what happened.
          </p>
        </header>
        <div className="engine">
          <div className="engine-col">
            <p className="compare-label">What goes in</p>
            <ul className="engine-list">
              {INPUTS.map((item) => (
                <li key={item.k}>
                  <strong>{item.k}</strong>
                  <span>{item.v}</span>
                </li>
              ))}
            </ul>
          </div>
          <div className="engine-core" aria-label="Agent pipeline">
            <p className="compare-label">Relief Copilot · LangGraph</p>
            <ol>
              {AGENTS.map((agent, i) => (
                <li key={agent}>
                  <span className="engine-idx">{String(i + 1).padStart(2, "0")}</span>
                  {agent}
                  {agent === "Integrity" ? <span className="engine-gate">Supervisor gate</span> : null}
                </li>
              ))}
            </ol>
            <p className="engine-foot">Qwen via Alibaba DashScope</p>
          </div>
          <div className="engine-col">
            <p className="compare-label">What comes out</p>
            <ul className="engine-list">
              {OUTCOMES.map((item) => (
                <li key={item.k}>
                  <strong>{item.k}</strong>
                  <span>{item.v}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </section>

      <section className="l-section" aria-labelledby="hitl-heading">
        <header className="l-head">
          <p className="eyebrow l-eyebrow l-eyebrow-hitl">Human in the loop</p>
          <h2 id="hitl-heading">Agents do the sorting. People make the hard calls.</h2>
        </header>
        <div className="rules">
          {RULES.map((rule) => (
            <div key={rule.when} className="rule">
              <p className="rule-when">{rule.when}</p>
              <p>{rule.then}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="l-section" aria-labelledby="numbers-heading">
        <header className="l-head">
          <p className="eyebrow l-eyebrow">Measured, not marketed</p>
          <h2 id="numbers-heading">What is built and tested today.</h2>
        </header>
        <dl className="numbers">
          {NUMBERS.map((item) => (
            <div key={item.label}>
              <dt>{item.label}</dt>
              <dd>{item.value}</dd>
            </div>
          ))}
        </dl>
        <p className="numbers-note">
          Prototype dataset for Lahore. Operational numbers such as time saved and duplicates
          caught come from the pilot.
        </p>
      </section>

      <section className="ngo-band" aria-labelledby="ngo-heading">
        <div>
          <p className="eyebrow">For NGOs</p>
          <h2 id="ngo-heading">One desk. Your rules.</h2>
          <p>
            Built for Alkhidmat, ready for any relief NGO. Requesters never pay; the desk is
            licensed to the organisation that runs it.
          </p>
          <Link className="btn btn-lg ngo-cta" href="/login">
            Open the staff desk
          </Link>
        </div>
        <ul>
          {NGO_POINTS.map((item) => (
            <li key={item.k}>
              <strong>{item.k}</strong>
              <span>{item.v}</span>
            </li>
          ))}
        </ul>
      </section>

      <section className="doors" aria-label="Choose a path">
        <Link className="door" href="/request">
          <strong>Need help</strong>
          <p className="muted" style={{ margin: 0 }}>
            Public request desk. Guest intake, live pipeline, ticket or supervisor hold.
          </p>
        </Link>
        <Link className="door" href="/status">
          <strong>Check status</strong>
          <p className="muted" style={{ margin: 0 }}>
            Track with your request number and the phone you gave. No account.
          </p>
        </Link>
        <Link className="door" href="/login">
          <strong>Run the desk</strong>
          <p className="muted" style={{ margin: 0 }}>
            Staff tickets, supervisor queue, metrics and case PDF.
          </p>
        </Link>
      </section>

      <StackStrip />
    </div>
  );
}
