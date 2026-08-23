"use client";

import { useEffect, useState } from "react";
import { getMetrics } from "@/lib/api";

type Metrics = {
  cases_today: number;
  cases_total: number;
  avg_time_to_ticket_ms: number;
  escalation_pct: number;
  pending_hitl: number;
  by_status: Record<string, number>;
  by_category: Record<string, number>;
};

export default function DashboardPage() {
  const [m, setM] = useState<Metrics | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    try {
      setError(null);
      setM(await getMetrics());
    } catch (e) {
      setError(e instanceof Error ? e.message : "Load failed");
    }
  }

  useEffect(() => {
    load();
    const t = setInterval(load, 8000);
    return () => clearInterval(t);
  }, []);

  return (
    <div>
      <h1>Ops dashboard</h1>
      <p className="muted">Impact visible — cases, speed, and escalations for judges and desk leads.</p>
      <div className="actions" style={{ margin: "0.75rem 0" }}>
        <button className="btn secondary" type="button" onClick={load}>
          Refresh
        </button>
      </div>
      {error && <p style={{ color: "var(--danger)" }}>{error}</p>}
      {m && (
        <>
          <div className="metrics">
            <div className="metric">
              <span className="muted">Cases today</span>
              <strong>{m.cases_today}</strong>
            </div>
            <div className="metric">
              <span className="muted">Total cases</span>
              <strong>{m.cases_total}</strong>
            </div>
            <div className="metric">
              <span className="muted">Avg time-to-ticket</span>
              <strong>{(m.avg_time_to_ticket_ms / 1000).toFixed(1)}s</strong>
            </div>
            <div className="metric">
              <span className="muted">Escalation %</span>
              <strong>{m.escalation_pct}%</strong>
            </div>
            <div className="metric">
              <span className="muted">Pending HITL</span>
              <strong>{m.pending_hitl}</strong>
            </div>
          </div>
          <div className="grid-2" style={{ marginTop: "1rem" }}>
            <section className="panel">
              <h2>By status</h2>
              <ul>
                {Object.entries(m.by_status).map(([k, v]) => (
                  <li key={k}>
                    {k}: <strong>{v}</strong>
                  </li>
                ))}
              </ul>
            </section>
            <section className="panel">
              <h2>By category</h2>
              <ul>
                {Object.entries(m.by_category).map(([k, v]) => (
                  <li key={k}>
                    {k}: <strong>{v}</strong>
                  </li>
                ))}
              </ul>
            </section>
          </div>
        </>
      )}
    </div>
  );
}
