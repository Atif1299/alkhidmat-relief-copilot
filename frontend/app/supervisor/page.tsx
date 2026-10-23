"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { AgentTrace } from "@/components/AgentTrace";
import { decideCase, getSupervisorQueue, type AgentStep } from "@/lib/api";
import { parseUtc, priorityTone, waitingFor } from "@/lib/format";

type QueueItem = {
  id: string;
  ticket_id?: string;
  raw_message: string;
  category?: string;
  priority?: string;
  location?: string;
  requester_phone?: string;
  risk_score?: number;
  duplicate_flag?: boolean;
  agent_trace?: AgentStep[];
  created_at?: string | null;
};

type Notice = { tone: "ok" | "warn"; text: string };

const REFRESH_MS = 12000;
const HIGH_RISK = 0.75;

function readableError(e: unknown, fallback: string): string {
  const raw = e instanceof Error ? e.message : fallback;
  if (raw === "Failed to fetch" || raw.includes("NetworkError")) {
    return "Can't reach the desk API. It may be starting up; the queue retries automatically.";
  }
  return raw;
}

/** Why Integrity sent the case here, from the fields the queue returns. */
function reasons(item: QueueItem): string[] {
  const out: string[] = [];
  if (item.priority === "critical") out.push("Critical priority");
  if (item.duplicate_flag) out.push("Same phone within 48 hours");
  if ((item.risk_score ?? 0) >= HIGH_RISK && !out.length) out.push("High risk score");
  if (!item.requester_phone) out.push("No phone number");
  return out.length ? out : ["Flagged by Integrity"];
}

function sortQueue(items: QueueItem[]): QueueItem[] {
  // Critical first, then whoever has waited longest.
  return [...items].sort((a, b) => {
    const crit = Number(b.priority === "critical") - Number(a.priority === "critical");
    if (crit) return crit;
    return (parseUtc(a.created_at)?.getTime() ?? 0) - (parseUtc(b.created_at)?.getTime() ?? 0);
  });
}

export default function SupervisorPage() {
  const [queue, setQueue] = useState<QueueItem[]>([]);
  const [notes, setNotes] = useState<Record<string, string>>({});
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState<string | null>(null);
  const [notice, setNotice] = useState<Notice | null>(null);
  const [loaded, setLoaded] = useState(false);
  const [updatedAt, setUpdatedAt] = useState<number | null>(null);
  const [now, setNow] = useState(() => Date.now());

  async function load() {
    try {
      setError(null);
      setQueue(await getSupervisorQueue());
      setUpdatedAt(Date.now());
    } catch (e) {
      setError(readableError(e, "Load failed"));
    } finally {
      setLoaded(true);
    }
  }

  useEffect(() => {
    load();
    const refresh = setInterval(load, REFRESH_MS);
    const tick = setInterval(() => setNow(Date.now()), 1000);
    return () => {
      clearInterval(refresh);
      clearInterval(tick);
    };
  }, []);

  async function onDecide(item: QueueItem, decision: "approve" | "reject") {
    setBusy(item.id);
    setNotice(null);
    try {
      const note = notes[item.id]?.trim() || undefined;
      const result = await decideCase(item.id, decision, note);
      const ticket = result.ticket_id || item.ticket_id || "The case";
      setNotice(
        decision === "approve"
          ? { tone: "ok", text: `${ticket} approved and dispatched. ${result.notification ?? ""}`.trim() }
          : { tone: "warn", text: `${ticket} rejected. The requester sees "Not approved" on the status page.` }
      );
      setNotes((prev) => {
        const next = { ...prev };
        delete next[item.id];
        return next;
      });
      await load();
    } catch (e) {
      setError(readableError(e, "Decision failed"));
      await load();
    } finally {
      setBusy(null);
    }
  }

  const sorted = useMemo(() => sortQueue(queue), [queue]);
  const critical = queue.filter((q) => q.priority === "critical").length;
  const duplicates = queue.filter((q) => q.duplicate_flag).length;
  const oldest = sorted.length
    ? sorted.reduce((a, b) =>
        (parseUtc(a.created_at)?.getTime() ?? Infinity) <= (parseUtc(b.created_at)?.getTime() ?? Infinity) ? a : b
      )
    : null;
  const secondsSinceUpdate = updatedAt ? Math.max(0, Math.round((now - updatedAt) / 1000)) : null;

  return (
    <div className="dash">
      <header className="dash-head">
        <div>
          <p className="eyebrow l-eyebrow l-eyebrow-hitl">Human in the loop</p>
          <h1>Supervisor queue</h1>
          <p className="muted" style={{ margin: 0 }}>
            Critical and flagged cases wait here. Nothing is matched or dispatched until you decide.
          </p>
        </div>
        <div className="dash-head-actions">
          <span className={`live-pill ${error ? "stale" : ""}`} role="status">
            <span className="live-dot" aria-hidden />
            {error
              ? "Connection lost"
              : secondsSinceUpdate == null
                ? "Connecting…"
                : `Live · updated ${secondsSinceUpdate}s ago`}
          </span>
          <button className="btn secondary" type="button" onClick={load}>
            Refresh
          </button>
        </div>
      </header>

      <section className="kpis hq-kpis" aria-label="Queue summary">
        <div className={`kpi ${queue.length ? "kpi-hitl" : ""}`}>
          <span className="kpi-label">Waiting</span>
          <strong>{queue.length}</strong>
          <span className="kpi-note">{queue.length ? "need a decision" : "queue is clear"}</span>
        </div>
        <div className="kpi">
          <span className="kpi-label">Critical</span>
          <strong>{critical}</strong>
          <span className="kpi-note">shown first</span>
        </div>
        <div className="kpi">
          <span className="kpi-label">Possible duplicates</span>
          <strong>{duplicates}</strong>
          <span className="kpi-note">same phone within 48 h</span>
        </div>
        <div className="kpi">
          <span className="kpi-label">Longest wait</span>
          <strong>{oldest ? waitingFor(oldest.created_at, now) : "—"}</strong>
          <span className="kpi-note">{oldest?.ticket_id ?? "nothing waiting"}</span>
        </div>
      </section>

      {notice && (
        <div className={`outcome-banner ${notice.tone}`} role="status">
          <p style={{ margin: 0 }}>{notice.text}</p>
        </div>
      )}
      {error && <p className="error">{error}</p>}

      {loaded && !queue.length && !error ? (
        <div className="panel empty-state hq-empty">
          <span className="hq-empty-mark" aria-hidden>
            ✓
          </span>
          <h2>Queue is clear</h2>
          <p className="muted">No cases are waiting for a decision. New flagged cases appear here automatically.</p>
          <div className="actions" style={{ justifyContent: "center" }}>
            <Link className="btn secondary" href="/tickets">
              View tickets
            </Link>
            <Link className="btn secondary" href="/dashboard">
              Open dashboard
            </Link>
          </div>
        </div>
      ) : null}

      <div className="hq-list">
        {sorted.map((item) => {
          const risk = item.risk_score ?? 0;
          const isBusy = busy === item.id;
          return (
            <article key={item.id} className={`panel hq-card ${item.priority === "critical" ? "critical" : ""}`}>
              <header className="hq-head">
                <div className="hq-tags">
                  <span className="mono hq-ticket">{item.ticket_id || "No ticket"}</span>
                  {item.priority ? (
                    <span className={`badge ${priorityTone(item.priority)}`}>{item.priority}</span>
                  ) : null}
                  <strong>{item.category || "Other"}</strong>
                  {item.duplicate_flag ? <span className="badge warn">duplicate</span> : null}
                </div>
                <span className="hq-wait">Waiting {waitingFor(item.created_at, now)}</span>
              </header>

              <div className="hq-body">
                <div className="hq-main">
                  <blockquote className="hq-message">{item.raw_message}</blockquote>
                  <dl className="hq-facts">
                    <div>
                      <dt>Area</dt>
                      <dd>{item.location || "—"}</dd>
                    </div>
                    <div>
                      <dt>Phone</dt>
                      <dd className="mono">{item.requester_phone || "—"}</dd>
                    </div>
                    <div>
                      <dt>Risk</dt>
                      <dd>
                        <span className="risk-meter" aria-hidden>
                          <span
                            className={`risk-fill ${risk >= HIGH_RISK ? "high" : ""}`}
                            style={{ width: `${Math.min(100, Math.round(risk * 100))}%` }}
                          />
                        </span>
                        <span className="mono">{risk.toFixed(2)}</span>
                      </dd>
                    </div>
                  </dl>
                  <div className="hq-reasons">
                    <span className="compare-label" style={{ margin: 0 }}>
                      Why it is here
                    </span>
                    <ul>
                      {reasons(item).map((r) => (
                        <li key={r}>{r}</li>
                      ))}
                    </ul>
                  </div>
                  <details className="hq-trace">
                    <summary>Agent trace ({(item.agent_trace || []).length} steps)</summary>
                    <AgentTrace steps={item.agent_trace || []} />
                  </details>
                </div>

                <aside className="hq-decide" aria-label="Decision">
                  <label htmlFor={`note-${item.id}`} className="compare-label">
                    Decision note
                  </label>
                  <textarea
                    id={`note-${item.id}`}
                    rows={3}
                    maxLength={1000}
                    placeholder="Optional. Saved on the case timeline."
                    value={notes[item.id] ?? ""}
                    onChange={(e) => setNotes((prev) => ({ ...prev, [item.id]: e.target.value }))}
                  />
                  <div className="hq-buttons">
                    <button className="btn" type="button" disabled={isBusy} onClick={() => onDecide(item, "approve")}>
                      {isBusy ? "Working…" : "Approve"}
                    </button>
                    <button
                      className="btn danger"
                      type="button"
                      disabled={isBusy}
                      onClick={() => onDecide(item, "reject")}
                    >
                      Reject
                    </button>
                  </div>
                  <p className="hq-hint">
                    Approve matches a resource and volunteer, then dispatches. Reject closes the case as not
                    approved.
                  </p>
                  <Link className="link-btn" href={`/cases/${item.id}`}>
                    Open case file →
                  </Link>
                </aside>
              </div>
            </article>
          );
        })}
      </div>
    </div>
  );
}
