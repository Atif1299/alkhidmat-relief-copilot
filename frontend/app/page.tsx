import Link from "next/link";
import { SitrepReplay } from "@/components/SitrepReplay";
import { StackStrip } from "@/components/StackStrip";

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
            Submit in Urdu or English. The desk runs Intake → Triage → Knowledge → Integrity →
            Matcher → Dispatch. You leave with a request number you can check later — or a
            supervisor hold. Never a silent queue.
          </p>
          <div className="landing-ctas">
            <Link className="btn btn-lg" href="/request">
              Request aid
            </Link>
            <Link className="btn secondary btn-lg" href="/status">
              Check status
            </Link>
            <Link className="btn secondary btn-lg" href="/login">
              Staff sign in
            </Link>
          </div>
        </div>
        <SitrepReplay />
      </section>

      <section className="landing-steps" aria-labelledby="how-heading">
        <h2 id="how-heading">How it works</h2>
        <ol className="landing-step-grid">
          <li>
            <span className="step-num">1</span>
            <strong>Citizen requests</strong>
            <p className="muted">Describe the need in Urdu or English — no account required.</p>
          </li>
          <li>
            <span className="step-num">2</span>
            <strong>Agents verify and match</strong>
            <p className="muted">Six-step pipeline: classify, check SOP, catch duplicates, match stock.</p>
          </li>
          <li>
            <span className="step-num">3</span>
            <strong>You know what is next</strong>
            <p className="muted">Request number plus phone — check status anytime, even after you leave.</p>
          </li>
        </ol>
      </section>

      <aside className="hitl-callout" aria-labelledby="hitl-heading">
        <span className="hitl-mark">HITL</span>
        <div>
          <h2 id="hitl-heading">Human when it matters</h2>
          <p className="muted" style={{ margin: 0 }}>
            Chest pain, duplicates, and high-risk integrity flags pause at Integrity. Dispatch
            does not fire until a supervisor approves. The saffron hold is the safety rail — not
            decoration.
          </p>
        </div>
      </aside>

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
            Staff tickets, HITL queue, metrics, and case PDF. JWT roles, not a chatbot.
          </p>
        </Link>
      </section>

      <StackStrip />
    </div>
  );
}
