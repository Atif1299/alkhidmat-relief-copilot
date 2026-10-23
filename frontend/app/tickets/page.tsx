"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { Fragment, useEffect, useMemo, useState } from "react";
import { AgentTrace } from "@/components/AgentTrace";
import { downloadCasePdf, listCases, type AgentStep } from "@/lib/api";
import { priorityTone, statusMeta, timeAgo } from "@/lib/format";

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
  created_at?: string | null;
};

const REFRESH_MS = 15000;

const TABS = [
  { key: "all", label: "All" },
  { key: "pending_hitl", label: "Waiting for supervisor" },
  { key: "dispatched", label: "Dispatched" },
  { key: "rejected", label: "Not approved" },
] as const;

type TabKey = (typeof TABS)[number]["key"];

export default function TicketsPage() {
  const router = useRouter();
  const [cases, setCases] = useState<CaseRow[]>([]);
  const [expanded, setExpanded] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loaded, setLoaded] = useState(false);
  const [updatedAt, setUpdatedAt] = useState<number | null>(null);
  const [now, setNow] = useState(() => Date.now());
  const [tab, setTab] = useState<TabKey>("all");
  const [category, setCategory] = useState("");
  const [query, setQuery] = useState("");

  async function load() {
    try {
      setError(null);
      setCases(await listCases());
      setUpdatedAt(Date.now());
    } catch (e) {
      setError(e instanceof Error ? e.message : "Load failed");
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

  const counts = useMemo(() => {
    const out: Record<string, number> = { all: cases.length };
    for (const c of cases) out[c.status] = (out[c.status] ?? 0) + 1;
    return out;
  }, [cases]);

  const categories = useMemo(
    () => [...new Set(cases.map((c) => c.category).filter(Boolean) as string[])].sort(),
    [cases]
  );

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    return cases.filter((c) => {
      if (tab !== "all" && c.status !== tab) return false;
      if (category && c.category !== category) return false;
      if (!q) return true;
      return [c.ticket_id, c.location, c.raw_message, c.requester_phone]
        .filter(Boolean)
        .some((v) => String(v).toLowerCase().includes(q));
    });
  }, [cases, tab, category, query]);

  const secondsSinceUpdate = updatedAt ? Math.max(0, Math.round((now - updatedAt) / 1000)) : null;
  const filtering = tab !== "all" || Boolean(category || query.trim());

  function openCase(id: string) {
    router.push(`/cases/${id}`);
  }

  return (
    <div className="dash">
      <header className="dash-head">
        <div>
          <p className="eyebrow l-eyebrow">Ops desk · Lahore</p>
          <h1>Tickets</h1>
          <p className="muted" style={{ margin: 0 }}>
            Every request the desk has handled. Click a row to open its case file.
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

      <div className="seg-tabs" role="tablist" aria-label="Filter by status">
        {TABS.map((t) => (
          <button
            key={t.key}
            type="button"
            role="tab"
            aria-selected={tab === t.key}
            className={`seg-tab ${tab === t.key ? "active" : ""}`}
            onClick={() => setTab(t.key)}
          >
            {t.label}
            <span className="seg-count">{counts[t.key] ?? 0}</span>
          </button>
        ))}
      </div>

      {error && <p className="error">{error}</p>}

      <section className="panel dash-panel" aria-label="Tickets">
        <header className="dash-panel-head dash-cases-head">
          <p className="muted" style={{ margin: 0 }}>
            Showing {filtered.length} of {cases.length}
          </p>
          <div className="dash-filters">
            <label className="sr-only" htmlFor="ticket-category">
              Category
            </label>
            <select
              id="ticket-category"
              className="dash-select"
              value={category}
              onChange={(e) => setCategory(e.target.value)}
            >
              <option value="">All categories</option>
              {categories.map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>
            <label className="sr-only" htmlFor="ticket-search">
              Search tickets
            </label>
            <input
              id="ticket-search"
              className="dash-search"
              type="search"
              placeholder="Search ticket, area, phone or message"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
          </div>
        </header>

        {loaded && !filtered.length ? (
          <div className="empty-state">
            {filtering ? (
              <>
                <p className="muted">No tickets match these filters.</p>
                <button
                  type="button"
                  className="btn secondary"
                  onClick={() => {
                    setTab("all");
                    setCategory("");
                    setQuery("");
                  }}
                >
                  Clear filters
                </button>
              </>
            ) : (
              <>
                <p className="muted">No tickets yet. Citizens submit from Request aid, or run a test intake.</p>
                <Link className="btn" href="/chat">
                  Open test intake
                </Link>
              </>
            )}
          </div>
        ) : (
          <div className="table-wrap">
            <table className="table dash-table tickets-table">
              <thead>
                <tr>
                  <th>Ticket</th>
                  <th>Request</th>
                  <th>Status</th>
                  <th>Category</th>
                  <th>Area</th>
                  <th>Received</th>
                  <th>
                    <span className="sr-only">Actions</span>
                  </th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((c) => {
                  const meta = statusMeta(c.status);
                  const open = expanded === c.id;
                  return (
                    <Fragment key={c.id}>
                      <tr
                        className={`row-link ${open ? "row-open" : ""}`}
                        tabIndex={0}
                        onClick={() => openCase(c.id)}
                        onKeyDown={(e) => {
                          if (e.key === "Enter") openCase(c.id);
                        }}
                      >
                        <td>
                          <span className="mono">{c.ticket_id || "—"}</span>
                          {c.duplicate_flag ? <span className="badge warn dup-badge">duplicate</span> : null}
                        </td>
                        <td className="req-cell">
                          <span className="req-text" title={c.raw_message}>
                            {c.raw_message}
                          </span>
                          {c.requester_phone ? <span className="req-sub mono">{c.requester_phone}</span> : null}
                        </td>
                        <td>
                          <span className={`badge ${meta.tone}`}>{meta.label}</span>
                        </td>
                        <td>
                          <span className="cat-cell">
                            {c.category || "—"}
                            {c.priority ? (
                              <span className={`badge ${priorityTone(c.priority)}`}>{c.priority}</span>
                            ) : null}
                          </span>
                        </td>
                        <td className="muted-cell">{c.location || "—"}</td>
                        <td className="muted-cell">{timeAgo(c.created_at, now)}</td>
                        <td>
                          <div className="row-actions">
                            <button
                              type="button"
                              className="icon-btn"
                              aria-expanded={open}
                              onClick={(e) => {
                                e.stopPropagation();
                                setExpanded(open ? null : c.id);
                              }}
                            >
                              Trace {open ? "▴" : "▾"}
                            </button>
                            <button
                              type="button"
                              className="icon-btn"
                              onClick={(e) => {
                                e.stopPropagation();
                                downloadCasePdf(c.id, `${c.ticket_id || c.id}.pdf`).catch(() =>
                                  setError("PDF export failed")
                                );
                              }}
                            >
                              PDF
                            </button>
                          </div>
                        </td>
                      </tr>
                      {open && (
                        <tr className="trace-row">
                          <td colSpan={7}>
                            <AgentTrace steps={c.agent_trace || []} />
                          </td>
                        </tr>
                      )}
                    </Fragment>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}
