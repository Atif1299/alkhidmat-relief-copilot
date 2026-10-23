"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useMemo, useState } from "react";
import { getAuthUser } from "@/lib/auth";
import { getMetrics, listCases } from "@/lib/api";

type Metrics = {
  cases_today: number;
  cases_total: number;
  avg_time_to_ticket_ms: number;
  escalation_pct: number;
  pending_hitl: number;
  by_status: Record<string, number>;
  by_category: Record<string, number>;
};

type CaseRow = {
  id: string;
  ticket_id?: string;
  status: string;
  category?: string;
  priority?: string;
  location?: string;
  raw_message: string;
  duplicate_flag?: boolean;
  time_to_ticket_ms?: number | null;
  created_at?: string | null;
};

const REFRESH_MS = 8000;

const STATUS_META: Record<string, { label: string; tone: string }> = {
  dispatched: { label: "Dispatched", tone: "ok" },
  pending_hitl: { label: "Waiting for supervisor", tone: "warn" },
  processing: { label: "Received", tone: "neutral" },
  open: { label: "Received", tone: "neutral" },
  rejected: { label: "Not approved", tone: "danger" },
  closed: { label: "Closed", tone: "neutral" },
};

const STATUS_ORDER = ["dispatched", "pending_hitl", "processing", "open", "rejected", "closed"];

function statusMeta(status: string) {
  return STATUS_META[status] ?? { label: status, tone: "neutral" };
}

function priorityTone(priority?: string) {
  if (priority === "critical") return "danger";
  if (priority === "high") return "warn";
  return "neutral";
}

/** API timestamps are naive UTC. */
function parseUtc(value?: string | null): Date | null {
  if (!value) return null;
  const hasZone = /[zZ]|[+-]\d\d:?\d\d$/.test(value);
  const d = new Date(hasZone ? value : `${value}Z`);
  return Number.isNaN(d.getTime()) ? null : d;
}

function timeAgo(value?: string | null, now = Date.now()): string {
  const d = parseUtc(value);
  if (!d) return "—";
  const s = Math.max(0, Math.round((now - d.getTime()) / 1000));
  if (s < 60) return "just now";
  const m = Math.round(s / 60);
  if (m < 60) return `${m} min ago`;
  const h = Math.round(m / 60);
  if (h < 24) return `${h} h ago`;
  return d.toLocaleDateString(undefined, { day: "numeric", month: "short" });
}

function seconds(ms?: number | null): string {
  if (ms == null) return "—";
  return `${(ms / 1000).toFixed(1)}s`;
}

export default function DashboardPage() {
  const router = useRouter();
  const [m, setM] = useState<Metrics | null>(null);
  const [cases, setCases] = useState<CaseRow[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isSupervisor, setIsSupervisor] = useState(false);
  const [updatedAt, setUpdatedAt] = useState<number | null>(null);
  const [now, setNow] = useState(() => Date.now());
  const [category, setCategory] = useState<string | null>(null);
  const [status, setStatus] = useState<string | null>(null);
  const [query, setQuery] = useState("");

  async function load() {
    try {
      setError(null);
      const [metrics, rows] = await Promise.all([getMetrics(), listCases()]);
      setM(metrics);
      setCases(rows);
      setUpdatedAt(Date.now());
    } catch (e) {
      setError(e instanceof Error ? e.message : "Load failed");
    }
  }

  useEffect(() => {
    setIsSupervisor(getAuthUser()?.role === "supervisor");
    load();
    const refresh = setInterval(load, REFRESH_MS);
    const tick = setInterval(() => setNow(Date.now()), 1000);
    return () => {
      clearInterval(refresh);
      clearInterval(tick);
    };
  }, []);

  const categories = useMemo(() => {
    const entries = Object.entries(m?.by_category ?? {}).sort((a, b) => b[1] - a[1]);
    const max = Math.max(1, ...entries.map(([, v]) => v));
    const total = entries.reduce((sum, [, v]) => sum + v, 0) || 1;
    return entries.map(([name, count]) => ({
      name,
      count,
      width: (count / max) * 100,
      share: Math.round((count / total) * 100),
    }));
  }, [m]);

  const statuses = useMemo(() => {
    const raw = m?.by_status ?? {};
    const total = Object.values(raw).reduce((sum, v) => sum + v, 0) || 1;
    return Object.entries(raw)
      .sort((a, b) => {
        const ia = STATUS_ORDER.indexOf(a[0]);
        const ib = STATUS_ORDER.indexOf(b[0]);
        return (ia < 0 ? 99 : ia) - (ib < 0 ? 99 : ib);
      })
      .map(([key, count]) => ({
        key,
        count,
        share: (count / total) * 100,
        ...statusMeta(key),
      }));
  }, [m]);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    return cases.filter((c) => {
      if (category && c.category !== category) return false;
      if (status && c.status !== status) return false;
      if (!q) return true;
      return [c.ticket_id, c.location, c.raw_message, c.category]
        .filter(Boolean)
        .some((v) => String(v).toLowerCase().includes(q));
    });
  }, [cases, category, status, query]);

  const filtering = Boolean(category || status || query.trim());
  const secondsSinceUpdate = updatedAt ? Math.max(0, Math.round((now - updatedAt) / 1000)) : null;

  return (
    <div className="dash">
      <header className="dash-head">
        <div>
          <p className="eyebrow l-eyebrow">Sitrep · Lahore desk</p>
          <h1>Ops dashboard</h1>
          <p className="muted" style={{ margin: 0 }}>
            Volume, speed and escalations. Click a category or status to filter the case list.
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

      {error && <p className="error">{error}</p>}

      {m && (
        <>
          <section className="kpis" aria-label="Key metrics">
            <div className="kpi">
              <span className="kpi-label">Cases today</span>
              <strong>{m.cases_today}</strong>
              <span className="kpi-note">of {m.cases_total} on record</span>
            </div>
            <div className="kpi">
              <span className="kpi-label">Avg time-to-ticket</span>
              <strong>{seconds(m.avg_time_to_ticket_ms)}</strong>
              <span className="kpi-note">request in, ticket out</span>
            </div>
            <div className="kpi">
              <span className="kpi-label">Escalation rate</span>
              <strong>{m.escalation_pct}%</strong>
              <span className="kpi-note">cases sent to a human</span>
            </div>
            <div className="kpi">
              <span className="kpi-label">Dispatched</span>
              <strong>{m.by_status.dispatched ?? 0}</strong>
              <span className="kpi-note">resource and volunteer assigned</span>
            </div>
            {isSupervisor ? (
              <Link
                href="/supervisor"
                className={`kpi kpi-link ${m.pending_hitl > 0 ? "kpi-hitl" : ""}`}
              >
                <span className="kpi-label">Waiting for supervisor</span>
                <strong>{m.pending_hitl}</strong>
                <span className="kpi-note">{m.pending_hitl > 0 ? "Review now →" : "Queue is clear"}</span>
              </Link>
            ) : (
              <div className={`kpi ${m.pending_hitl > 0 ? "kpi-hitl" : ""}`}>
                <span className="kpi-label">Waiting for supervisor</span>
                <strong>{m.pending_hitl}</strong>
                <span className="kpi-note">{m.pending_hitl > 0 ? "awaiting a decision" : "Queue is clear"}</span>
              </div>
            )}
          </section>

          <div className="dash-grid">
            <section className="panel dash-panel" aria-labelledby="cat-heading">
              <header className="dash-panel-head">
                <h2 id="cat-heading">Cases by category</h2>
                {category && (
                  <button type="button" className="link-btn" onClick={() => setCategory(null)}>
                    Clear
                  </button>
                )}
              </header>
              {categories.length === 0 ? (
                <p className="muted">No cases yet.</p>
              ) : (
                <ul className="bars">
                  {categories.map((c) => {
                    const active = category === c.name;
                    const dimmed = category !== null && !active;
                    return (
                      <li key={c.name}>
                        <button
                          type="button"
                          className={`bar-row ${active ? "active" : ""} ${dimmed ? "dimmed" : ""}`}
                          aria-pressed={active}
                          title={`${c.name}: ${c.count} cases, ${c.share}% of all cases`}
                          onClick={() => setCategory(active ? null : c.name)}
                        >
                          <span className="bar-name">{c.name}</span>
                          <span className="bar-track">
                            <span className="bar-fill" style={{ width: `${c.width}%` }} />
                          </span>
                          <span className="bar-value">
                            {c.count}
                            <span className="bar-share">{c.share}%</span>
                          </span>
                        </button>
                      </li>
                    );
                  })}
                </ul>
              )}
            </section>

            <section className="panel dash-panel" aria-labelledby="status-heading">
              <header className="dash-panel-head">
                <h2 id="status-heading">Where cases stand</h2>
                {status && (
                  <button type="button" className="link-btn" onClick={() => setStatus(null)}>
                    Clear
                  </button>
                )}
              </header>
              <div className="status-bar" role="img" aria-label="Share of cases by status">
                {statuses.map((s) => (
                  <span
                    key={s.key}
                    className={`status-seg tone-${s.tone} ${status && status !== s.key ? "dimmed" : ""}`}
                    style={{ width: `${s.share}%` }}
                    title={`${s.label}: ${s.count}`}
                  />
                ))}
              </div>
              <ul className="status-rows">
                {statuses.map((s) => {
                  const active = status === s.key;
                  return (
                    <li key={s.key}>
                      <button
                        type="button"
                        className={`status-row ${active ? "active" : ""}`}
                        aria-pressed={active}
                        onClick={() => setStatus(active ? null : s.key)}
                      >
                        <span className={`status-swatch tone-${s.tone}`} aria-hidden />
                        <span className="status-name">{s.label}</span>
                        <span className="status-count">{s.count}</span>
                        <span className="status-share">{Math.round(s.share)}%</span>
                      </button>
                    </li>
                  );
                })}
              </ul>
            </section>
          </div>
        </>
      )}

      <section className="panel dash-panel dash-cases" aria-labelledby="cases-heading">
        <header className="dash-panel-head dash-cases-head">
          <div>
            <h2 id="cases-heading">Recent cases</h2>
            <p className="muted" style={{ margin: 0 }}>
              Showing {filtered.length} of {cases.length} latest
            </p>
          </div>
          <div className="dash-filters">
            {category && (
              <button type="button" className="filter-chip" onClick={() => setCategory(null)}>
                {category} <span aria-hidden>×</span>
                <span className="sr-only">Remove category filter</span>
              </button>
            )}
            {status && (
              <button type="button" className="filter-chip" onClick={() => setStatus(null)}>
                {statusMeta(status).label} <span aria-hidden>×</span>
                <span className="sr-only">Remove status filter</span>
              </button>
            )}
            <label className="sr-only" htmlFor="case-search">
              Search cases
            </label>
            <input
              id="case-search"
              className="dash-search"
              type="search"
              placeholder="Search ticket, area or message"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
          </div>
        </header>

        {filtered.length === 0 ? (
          <div className="empty-state">
            <p className="muted">
              {filtering ? "No cases match these filters." : "No cases yet."}
            </p>
            {filtering && (
              <button
                type="button"
                className="btn secondary"
                onClick={() => {
                  setCategory(null);
                  setStatus(null);
                  setQuery("");
                }}
              >
                Clear filters
              </button>
            )}
          </div>
        ) : (
          <div className="table-wrap">
            <table className="table dash-table">
              <thead>
                <tr>
                  <th>Ticket</th>
                  <th>Received</th>
                  <th>Category</th>
                  <th>Priority</th>
                  <th>Status</th>
                  <th>Area</th>
                  <th className="num">To ticket</th>
                </tr>
              </thead>
              <tbody>
                {filtered.slice(0, 25).map((c) => {
                  const meta = statusMeta(c.status);
                  return (
                    <tr
                      key={c.id}
                      className="row-link"
                      tabIndex={0}
                      onClick={() => router.push(`/cases/${c.id}`)}
                      onKeyDown={(e) => {
                        if (e.key === "Enter") router.push(`/cases/${c.id}`);
                      }}
                    >
                      <td>
                        <span className="mono">{c.ticket_id || "—"}</span>
                        {c.duplicate_flag ? <span className="badge warn dup-badge">duplicate</span> : null}
                      </td>
                      <td className="muted-cell">{timeAgo(c.created_at, now)}</td>
                      <td>{c.category || "—"}</td>
                      <td>
                        {c.priority ? (
                          <span className={`badge ${priorityTone(c.priority)}`}>{c.priority}</span>
                        ) : (
                          "—"
                        )}
                      </td>
                      <td>
                        <span className={`badge ${meta.tone}`}>{meta.label}</span>
                      </td>
                      <td className="muted-cell">{c.location || "—"}</td>
                      <td className="num mono">{seconds(c.time_to_ticket_ms)}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
        {filtered.length > 25 && (
          <p className="muted" style={{ margin: "0.75rem 0 0" }}>
            Showing the 25 most recent. <Link href="/tickets">Open all tickets →</Link>
          </p>
        )}
      </section>
    </div>
  );
}
