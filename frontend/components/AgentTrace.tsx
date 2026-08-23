"use client";

import type { AgentStep } from "@/lib/api";

export function AgentTrace({ steps }: { steps: AgentStep[] }) {
  if (!steps.length) {
    return <p className="muted">Agent steps will appear here as the desk runs…</p>;
  }
  return (
    <ul className="trace">
      {steps.map((s, i) => (
        <li key={`${s.agent}-${s.action}-${i}`}>
          <strong>{s.agent}</strong> · {s.action}
          <div className="muted">{s.detail}</div>
        </li>
      ))}
    </ul>
  );
}
