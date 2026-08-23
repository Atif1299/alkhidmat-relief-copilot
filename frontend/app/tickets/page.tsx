"use client";

import { Fragment, useEffect, useState } from "react";
import { AgentTrace } from "@/components/AgentTrace";
import { listCases, type AgentStep } from "@/lib/api";

type CaseRow = {
  id: string;
  ticket_id?: string;
  status: string;
  category?: string;
  priority?: string;
  location?: string;
  requester_phone?: string;
  raw_message: string;
  agent_trace?: AgentStep[];
  duplicate_flag?: boolean;
};

export default function TicketsPage() {
  const [cases, setCases] = useState<CaseRow[]>([]);
  const [expanded, setExpanded] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    try {
      setError(null);
      setCases(await listCases());
    } catch (e) {
      setError(e instanceof Error ? e.message : "Load failed");
    }
  }

  useEffect(() => {
    load();
  }, []);

  return (
    <div>
      <h1>Ops tickets</h1>
      <p className="muted">All relief cases routed by the multi-agent desk.</p>
      <div className="actions" style={{ margin: "0.75rem 0" }}>
        <button className="btn secondary" type="button" onClick={load}>
          Refresh
        </button>
      </div>
      {error && <p style={{ color: "var(--danger)" }}>{error}</p>}
      <div className="panel">
        <table className="table">
          <thead>
            <tr>
              <th>Ticket</th>
              <th>Status</th>
              <th>Category</th>
              <th>Location</th>
              <th>Phone</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {cases.map((c) => (
              <Fragment key={c.id}>
                <tr>
                  <td>
                    <strong>{c.ticket_id || "—"}</strong>
                    <div className="muted" style={{ maxWidth: 220 }}>
                      {c.raw_message.slice(0, 80)}
                    </div>
                  </td>
                  <td>
                    <span
                      className={`badge ${
                        c.status === "dispatched"
                          ? "ok"
                          : c.status === "pending_hitl"
                            ? "warn"
                            : c.status === "rejected"
                              ? "danger"
                              : "neutral"
                      }`}
                    >
                      {c.status}
                    </span>
                    {c.duplicate_flag ? " !" : ""}
                  </td>
                  <td>
                    {c.category}
                    <div className="muted">{c.priority}</div>
                  </td>
                  <td>{c.location}</td>
                  <td>{c.requester_phone}</td>
                  <td>
                    <button
                      className="chip"
                      type="button"
                      onClick={() => setExpanded(expanded === c.id ? null : c.id)}
                    >
                      Trace
                    </button>
                  </td>
                </tr>
                {expanded === c.id && (
                  <tr>
                    <td colSpan={6}>
                      <AgentTrace steps={c.agent_trace || []} />
                    </td>
                  </tr>
                )}
              </Fragment>
            ))}
          </tbody>
        </table>
        {!cases.length && !error && <p className="muted">No tickets yet.</p>}
      </div>
    </div>
  );
}
