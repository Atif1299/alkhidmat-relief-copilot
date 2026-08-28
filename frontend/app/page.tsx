import Link from "next/link";

export default function HomePage() {
  return (
    <div className="landing">
      <section className="landing-hero">
        <p className="eyebrow">Alkhidmat-style relief operations</p>
        <h1>
          From an aid request to a verified ticket —
          <span className="hero-accent"> with a human when it matters</span>
        </h1>
        <p className="landing-lede">
          Submit in Urdu or English. Multi-agent intake classifies, checks duplicates, matches
          resources, and opens a ticket — or pauses for supervisor approval on critical cases.
        </p>
        <div className="landing-ctas">
          <Link className="btn btn-lg" href="/request">
            Request aid
          </Link>
          <Link className="btn secondary btn-lg" href="/login">
            Staff sign in
          </Link>
        </div>
      </section>

      <section className="landing-steps" aria-labelledby="how-heading">
        <h2 id="how-heading">How it works</h2>
        <ol className="landing-step-grid">
          <li>
            <span className="step-num">1</span>
            <strong>Citizen requests</strong>
            <p className="muted">Describe the need — no account required.</p>
          </li>
          <li>
            <span className="step-num">2</span>
            <strong>Agents verify &amp; match</strong>
            <p className="muted">Intake → Triage → Knowledge → Integrity → Matcher → Dispatch.</p>
          </li>
          <li>
            <span className="step-num">3</span>
            <strong>You know what&apos;s next</strong>
            <p className="muted">Ticket ID, resource match, or waiting for supervisor.</p>
          </li>
        </ol>
      </section>

      <section className="landing-trust panel">
        <h2>Built for the desk</h2>
        <p className="muted">
          Desk operators see every case with an agent trace. Supervisors approve high-risk or
          duplicate cases before dispatch. Citizens never need a staff login.
        </p>
        <div className="landing-ctas" style={{ marginTop: "1rem" }}>
          <Link className="btn" href="/request">
            Start a request
          </Link>
        </div>
      </section>
    </div>
  );
}
