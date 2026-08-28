"use client";

import Link from "next/link";
import { Fragment, useEffect, useState } from "react";
import { AgentTrace } from "@/components/AgentTrace";
import { downloadCasePdf, listCases, type AgentStep } from "@/lib/api";

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

function statusBadge(status: string) {
  if (status === "dispatched") return "ok";
  if (status === "pending_hitl") return "warn";
  if (status === "rejected") return "danger";
  return "neutral";
}

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
      {error && <p className="error">{error}</p>}
      <div className="panel">
        {!cases.length && !error ? (
          <div className="empty-state">
            <p className="muted">No tickets yet. Citizens submit from Request aid — or run a test intake.</p>
            <Link className="btn" href="/chat">
              Open test intake
            </Link>
          </div>
        ) : (
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
                      <Link href={`/cases/${c.id}`}>
                        <strong>{c.ticket_id || "—"}</strong>
                      </Link>
                      <div className="muted" style={{ maxWidth: 220 }}>
                        {c.raw_message.slice(0, 80)}
                      </div>
                    </td>
                    <td>
                      <span className={`badge ${statusBadge(c.status)}`}>{c.status}</span>
                      {c.duplicate_flag ? (
                        <span className="badge warn" style={{ marginLeft: 4 }}>
                          dup
                        </span>
                      ) : null}
                    </td>
                    <td>
                      {c.category}
                      <div className="muted">{c.priority}</div>
                    </td>
                    <td>{c.location}</td>
                    <td>{c.requester_phone}</td>
                    <td>
                      <div className="actions">
                        <Link className="chip" href={`/cases/${c.id}`}>
                          Detail
                        </Link>
                        <button
                          className="chip"
                          type="button"
                          onClick={() => setExpanded(expanded === c.id ? null : c.id)}
                        >
                          Trace
                        </button>
                        <button
                          className="chip"
                          type="button"
                          onClick={() =>
                            downloadCasePdf(c.id, `${c.ticket_id || c.id}.pdf`).catch(() =>
                              setError("PDF export failed")
                            )
                          }
                        >
                          PDF
                        </button>
                      </div>
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
        )}
      </div>
    </div>
  );
}
