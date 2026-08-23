"use client";

import { useEffect, useState } from "react";
import { AgentTrace } from "@/components/AgentTrace";
import { decideCase, getSupervisorQueue, type AgentStep } from "@/lib/api";

type QueueItem = {
  id: string;
  raw_message: string;
  category?: string;
  priority?: string;
  location?: string;
  requester_phone?: string;
  risk_score?: number;
  duplicate_flag?: boolean;
  agent_trace?: AgentStep[];
};

export default function SupervisorPage() {
  const [queue, setQueue] = useState<QueueItem[]>([]);
  const [note, setNote] = useState("Verified by supervisor");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState<string | null>(null);

  async function load() {
    try {
      setError(null);
      setQueue(await getSupervisorQueue());
    } catch (e) {
      setError(e instanceof Error ? e.message : "Load failed");
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function onDecide(id: string, decision: "approve" | "reject") {
    setBusy(id);
    try {
      await decideCase(id, decision, note);
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Decision failed");
    } finally {
      setBusy(null);
    }
  }

  return (
    <div>
      <h1>Supervisor HITL</h1>
      <p className="muted">
        Critical and high-risk cases pause here until a human approves or rejects.
      </p>
      <div className="panel" style={{ marginTop: "1rem", marginBottom: "1rem" }}>
        <label className="muted">Decision note</label>
        <input value={note} onChange={(e) => setNote(e.target.value)} />
      </div>
      <div className="actions" style={{ marginBottom: "0.75rem" }}>
        <button className="btn secondary" type="button" onClick={load}>
          Refresh queue
        </button>
      </div>
      {error && <p style={{ color: "var(--danger)" }}>{error}</p>}
      {!queue.length && !error && <p className="muted">No pending cases.</p>}
      <div style={{ display: "grid", gap: "0.85rem" }}>
        {queue.map((item) => (
          <article key={item.id} className="panel">
            <div className="actions" style={{ justifyContent: "space-between" }}>
              <div>
                <span className={`badge ${item.priority === "critical" ? "danger" : "warn"}`}>
                  {item.priority}
                </span>{" "}
                <strong>{item.category}</strong>
                {item.duplicate_flag ? " · duplicate" : ""}
                <div className="muted">
                  Risk {(item.risk_score ?? 0).toFixed(2)} · {item.location} · {item.requester_phone}
                </div>
              </div>
              <div className="actions">
                <button
                  className="btn"
                  type="button"
                  disabled={busy === item.id}
                  onClick={() => onDecide(item.id, "approve")}
                >
                  Approve
                </button>
                <button
                  className="btn danger"
                  type="button"
                  disabled={busy === item.id}
                  onClick={() => onDecide(item.id, "reject")}
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
