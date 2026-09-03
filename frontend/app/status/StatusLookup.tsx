"use client";

import { FormEvent, useState } from "react";
import Link from "next/link";
import { CaseTimeline } from "@/components/CaseTimeline";
import { lookupStatus, type PublicStatus } from "@/lib/api";

const DEMOS = [
  { label: "Dispatched · food", ticket: "AKD-SEED-001", phone: "03001234567" },
  { label: "Waiting · medical", ticket: "AKD-SEED-006", phone: "03019991111" },
];

function bannerClass(status?: string) {
  if (status === "dispatched" || status === "closed") return "ok";
  if (status === "pending_hitl" || status === "processing") return "warn";
  if (status === "rejected") return "warn";
  return "";
}

export function StatusLookup({ initialTicket = "" }: { initialTicket?: string }) {
  const [ticket, setTicket] = useState(initialTicket);
  const [phone, setPhone] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<PublicStatus | null>(null);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    setResult(null);
    try {
      const data = await lookupStatus(ticket, phone);
      setResult(data);
    } catch (err) {
      const raw = err instanceof Error ? err.message : "Lookup failed";
      if (raw.includes("not found") || raw.includes("404")) {
        setError("Request not found. Check the number and the phone used on the request.");
      } else if (raw.includes("422")) {
        setError("Enter a request number and a phone with at least 6 digits.");
      } else {
        setError(raw);
      }
    } finally {
      setBusy(false);
    }
  }

  return (
    <div>
      <header className="page-head">
        <p className="eyebrow">Public track · no account</p>
        <h1>Check status</h1>
        <p className="urdu hero-urdu" lang="ur" style={{ fontSize: "1.05rem", margin: "0 0 0.4rem" }}>
          نمبر اور فون سے درخواست چیک کریں
        </p>
        <p className="muted" style={{ margin: 0 }}>
          Use the request number from submit plus the same phone you gave. Wrong pair returns not
          found — we do not list every request on a number.
        </p>
      </header>

      <div className="grid-2" style={{ marginTop: "1rem" }}>
        <section className="panel">
          <h2>Look up a request</h2>
          <div className="chips">
            {DEMOS.map((demo) => (
              <button
                key={demo.ticket}
                type="button"
                className={ticket === demo.ticket ? "chip active" : "chip"}
                onClick={() => {
                  setTicket(demo.ticket);
                  setPhone(demo.phone);
                  setError(null);
                }}
              >
                {demo.label}
              </button>
            ))}
          </div>
          <form onSubmit={onSubmit} className="stack" style={{ marginTop: "0.85rem" }}>
            <label htmlFor="status-ticket">
              Request number
              <input
                id="status-ticket"
                value={ticket}
                onChange={(e) => setTicket(e.target.value)}
                autoComplete="off"
                placeholder="AKD-…"
              />
            </label>
            <label htmlFor="status-phone">
              Phone on the request
              <input
                id="status-phone"
                type="tel"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                autoComplete="tel"
                placeholder="03xx…"
              />
            </label>
            <div className="actions">
              <button className="btn" type="submit" disabled={busy || !ticket.trim() || !phone.trim()}>
                {busy ? "Checking…" : "Check status"}
              </button>
            </div>
          </form>
          {error && <p className="error">{error}</p>}
        </section>

        <aside className="panel">
          <h2>Sitrep</h2>
          {!result && !error && (
            <p className="muted" style={{ margin: 0 }}>
              Submit a lookup, or use a demo chip. Seed food ticket is{" "}
              <code className="ticket-stamp" style={{ fontSize: "0.78rem" }}>
                AKD-SEED-001
              </code>
              .
            </p>
          )}
          {result && (
            <>
              <div className={`outcome-banner ${bannerClass(result.status)}`} role="status">
                <strong>{result.status === "pending_hitl" ? "Waiting for supervisor" : result.status}</strong>
                <p>{result.next_action}</p>
                <code className="ticket-stamp">{result.ticket_id}</code>
                {result.category && <p className="muted">Category: {result.category}</p>}
                {(result.resource_name || result.volunteer_name) && (
                  <p className="muted">
                    {[result.resource_name, result.volunteer_name].filter(Boolean).join(" · ")}
                  </p>
                )}
              </div>
              <h3 style={{ marginTop: "1.1rem" }}>Timeline</h3>
              <CaseTimeline stages={result.timeline} />
            </>
          )}
        </aside>
      </div>

      <p className="muted" style={{ marginTop: "1.5rem" }}>
        Need help? <Link href="/request">Request aid</Link>
      </p>
    </div>
  );
}
