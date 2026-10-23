"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { AgentTrace } from "@/components/AgentTrace";
import { decideCase, getSupervisorQueue, type AgentStep } from "@/lib/api";

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
};

type Notice = { tone: "ok" | "warn"; text: string };

function readableError(e: unknown, fallback: string): string {
  const raw = e instanceof Error ? e.message : fallback;
  if (raw === "Failed to fetch" || raw.includes("NetworkError")) {
    return "Can't reach the desk API. It may be starting up; the queue retries automatically.";
  }
  return raw;
}

export default function SupervisorPage() {
  const [queue, setQueue] = useState<QueueItem[]>([]);
  const [note, setNote] = useState("Verified by supervisor");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState<string | null>(null);
  const [notice, setNotice] = useState<Notice | null>(null);

  async function load() {
    try {
      setError(null);
      setQueue(await getSupervisorQueue());
    } catch (e) {
      setError(readableError(e, "Load failed"));
    }
  }

  useEffect(() => {
    load();
    const t = setInterval(load, 12000);
    return () => clearInterval(t);
  }, []);

  async function onDecide(item: QueueItem, decision: "approve" | "reject") {
    setBusy(item.id);
    setNotice(null);
    try {
      const result = await decideCase(item.id, decision, note);
      const ticket = result.ticket_id || item.ticket_id || "The case";
      setNotice(
        decision === "approve"
          ? { tone: "ok", text: `${ticket} approved and dispatched. ${result.notification ?? ""}`.trim() }
          : { tone: "warn", text: `${ticket} rejected. The requester sees "Not approved" on the status page.` }
      );
      await load();
    } catch (e) {
      setError(readableError(e, "Decision failed"));
      await load();
    } finally {
      setBusy(null);
    }
  }

  return (
    <div>
      <header className="page-head">
        <p className="eyebrow">Human in the loop</p>
        <h1>Supervisor queue</h1>
        <p className="muted" style={{ margin: 0 }}>
          Critical and high-risk cases pause here until a human approves or rejects.
        </p>
      </header>
      <div className="panel" style={{ marginTop: "1rem", marginBottom: "1rem" }}>
        <label htmlFor="decision-note" className="muted">
          Decision note
        </label>
        <input
          id="decision-note"
          value={note}
          onChange={(e) => setNote(e.target.value)}
          style={{ marginTop: "0.35rem" }}
        />
      </div>
      <div className="actions" style={{ marginBottom: "0.75rem" }}>
        <button className="btn secondary" type="button" onClick={load}>
          Refresh queue
        </button>
      </div>
      {notice && (
        <div className={`outcome-banner ${notice.tone}`} role="status" style={{ marginBottom: "0.85rem" }}>
          <p style={{ margin: 0 }}>{notice.text}</p>
        </div>
      )}
      {error && <p className="error">{error}</p>}
      {!queue.length && !error && (
        <div className="panel empty-state">
          <p className="muted">No pending cases. Queue is clear.</p>
          <Link className="btn secondary" href="/tickets">
            View tickets
          </Link>
        </div>
      )}
      <div style={{ display: "grid", gap: "0.85rem" }}>
        {queue.map((item) => (
          <article key={item.id} className="panel hitl-case">
            <div className="actions" style={{ justifyContent: "space-between" }}>
              <div>
                <span className={`badge ${item.priority === "critical" ? "danger" : "warn"}`}>
                  {item.priority}
                </span>{" "}
                <strong>{item.category}</strong>
                {item.duplicate_flag ? (
                  <span className="badge warn" style={{ marginLeft: 6 }}>
                    duplicate
                  </span>
                ) : null}
                <div className="muted">
                  {item.ticket_id ? <span className="mono">{item.ticket_id} · </span> : null}
                  Risk {(item.risk_score ?? 0).toFixed(2)} · {item.location} · {item.requester_phone}
                </div>
              </div>
              <div className="actions">
                <Link className="chip" href={`/cases/${item.id}`}>
                  Case detail
                </Link>
                <button
                  className="btn"
                  type="button"
                  disabled={busy === item.id}
                  onClick={() => onDecide(item, "approve")}
                >
                  Approve
                </button>
                <button
                  className="btn danger"
                  type="button"
                  disabled={busy === item.id}
                  onClick={() => onDecide(item, "reject")}
                >
                  Reject
                </button>
              </div>
            </div>
            <p style={{ marginTop: "0.75rem" }}>{item.raw_message}</p>
            <AgentTrace steps={item.agent_trace || []} />
          </article>
        ))}
      </div>
    </div>
  );
}
