"use client";

import type { AgentStep } from "@/lib/api";

function dedupeSteps(steps: AgentStep[]): AgentStep[] {
  const seen = new Set<string>();
  const out: AgentStep[] = [];
  for (const s of steps) {
    const key = `${s.agent ?? ""}|${s.action ?? ""}|${s.detail ?? ""}`;
    if (seen.has(key)) continue;
    seen.add(key);
    out.push(s);
  }
  return out;
}

export function AgentTrace({ steps }: { steps: AgentStep[] }) {
  const unique = dedupeSteps(steps);
  if (!unique.length) {
    return <p className="muted">Agent steps will appear here as the desk runs…</p>;
  }
  return (
    <ul className="trace">
      {unique.map((s, i) => (
        <li key={`${s.agent}-${s.action}-${i}`}>
          <strong>{s.agent}</strong> · {s.action}
          <div className="muted">{s.detail}</div>
        </li>
      ))}
    </ul>
  );
}
