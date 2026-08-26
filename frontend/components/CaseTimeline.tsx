"use client";

export type TimelineStage = {
  key: string;
  label: string;
  state: "done" | "active" | "pending" | "skipped";
  detail?: string | null;
  at?: string | number | null;
};

export function CaseTimeline({ stages }: { stages?: TimelineStage[] | null }) {
  if (!stages?.length) {
    return <p className="muted">Timeline not available yet.</p>;
  }
  return (
    <ol className="timeline">
      {stages
        .filter((s) => s.state !== "skipped")
        .map((stage) => (
          <li key={stage.key} className={`timeline-item ${stage.state}`}>
            <div className="timeline-dot" />
            <div>
              <strong>{stage.label}</strong>
              <span className="badge neutral" style={{ marginLeft: 8 }}>
                {stage.state}
              </span>
              {stage.detail && <p className="muted">{stage.detail}</p>}
            </div>
          </li>
        ))}
    </ol>
  );
}
