"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { AgentTrace } from "@/components/AgentTrace";
import { CaseTimeline, type TimelineStage } from "@/components/CaseTimeline";
import { SopCitations, type SopHit } from "@/components/SopCitations";
import {
  caseExportPdfUrl,
  getCase,
  type AgentStep,
} from "@/lib/api";

type CaseDetail = {
  id: string;
  ticket_id?: string;
  status: string;
  category?: string;
  priority?: string;
  location?: string;
  requester_phone?: string;
  requester_name?: string;
  raw_message: string;
  need_summary?: string;
  hitl_decision?: string;
  hitl_note?: string;
  agent_trace?: AgentStep[];
  sop_hits?: SopHit[];
  timeline?: TimelineStage[];
  duplicate_flag?: boolean;
  risk_score?: number;
};

export default function CaseDetailPage() {
  const params = useParams();
  const caseId = String(params.id || "");
  const [data, setData] = useState<CaseDetail | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!caseId) return;
    getCase(caseId)
      .then(setData)
      .catch((e) => setError(e instanceof Error ? e.message : "Load failed"));
  }, [caseId]);

  if (error) {
    return (
      <div>
        <p style={{ color: "var(--danger)" }}>{error}</p>
        <Link href="/tickets">Back to tickets</Link>
      </div>
    );
  }

  if (!data) {
    return <p className="muted">Loading case…</p>;
  }

  return (
    <div>
      <p className="muted">
        <Link href="/tickets">← Tickets</Link>
      </p>
      <h1>{data.ticket_id || data.id}</h1>
      <p className="muted">
        {data.category} · {data.priority} · risk {data.risk_score ?? "—"}
        {data.duplicate_flag ? " · duplicate" : ""}
      </p>
      <div className="actions" style={{ margin: "0.75rem 0" }}>
        <a className="btn" href={caseExportPdfUrl(data.id)} target="_blank" rel="noreferrer">
          Export PDF
        </a>
        {data.status === "pending_hitl" && (
          <Link className="btn secondary" href="/supervisor">
            Open supervisor
          </Link>
        )}
      </div>

      <div className="grid-2">
        <section className="panel">
          <h2>Request</h2>
          <p>{data.raw_message}</p>
          <p className="muted">
            {data.requester_name} · {data.requester_phone} · {data.location}
          </p>
          <span
            className={`badge ${
              data.status === "dispatched"
                ? "ok"
                : data.status === "pending_hitl"
                  ? "warn"
                  : data.status === "rejected"
                    ? "danger"
                    : "neutral"
            }`}
          >
            {data.status}
          </span>
          {data.hitl_decision && (
            <p className="muted">
              Supervisor: {data.hitl_decision} — {data.hitl_note || "—"}
            </p>
          )}
          <h2 style={{ marginTop: "1.25rem" }}>SOP citations</h2>
          <SopCitations hits={data.sop_hits} />
        </section>
        <section className="panel">
          <h2>Timeline</h2>
          <CaseTimeline stages={data.timeline} />
          <h2 style={{ marginTop: "1.25rem" }}>Agent trace</h2>
          <AgentTrace steps={data.agent_trace || []} />
        </section>
      </div>
    </div>
  );
}
