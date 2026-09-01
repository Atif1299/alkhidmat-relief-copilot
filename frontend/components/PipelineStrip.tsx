"use client";

import type { AgentStep } from "@/lib/api";

const STAGES = ["Intake", "Triage", "Knowledge", "Integrity", "Matcher", "Dispatch"] as const;

function normalizeAgent(name: string): string {
  const n = name.toLowerCase();
  if (n.includes("intake")) return "Intake";
  if (n.includes("triage")) return "Triage";
  if (n.includes("knowledge") || n.includes("rag")) return "Knowledge";
  if (n.includes("integrity")) return "Integrity";
  if (n.includes("match")) return "Matcher";
  if (n.includes("dispatch")) return "Dispatch";
  if (n.includes("hitl") || n.includes("supervisor")) return "Integrity";
  return name;
}

export function PipelineStrip({
  steps,
  busy,
  status,
}: {
  steps: AgentStep[];
  busy?: boolean;
  status?: string | null;
}) {
  const done = new Set(steps.map((s) => normalizeAgent(s.agent)));
  let lastDone = -1;
  for (let i = 0; i < STAGES.length; i++) {
    if (done.has(STAGES[i])) lastDone = i;
  }

  const hitlWait = status === "pending_hitl";
  const dispatched = status === "dispatched";
  const integrityIdx = STAGES.indexOf("Integrity");

  let runningIndex = -1;
  if (busy && !hitlWait && !dispatched) {
    runningIndex = lastDone < 0 ? 0 : Math.min(lastDone + 1, STAGES.length - 1);
  }

  return (
    <ol className="pipeline-strip" aria-label="Agent pipeline">
      {STAGES.map((stage, i) => {
        let state = "pending";
        if (dispatched || i < lastDone || (i === lastDone && !hitlWait)) {
          state = "done";
        }
        if (hitlWait && i < integrityIdx) state = "done";
        if (hitlWait && i === integrityIdx) state = "paused";
        if (runningIndex === i) state = "active";
        return (
          <li key={stage} className={`pipeline-step ${state}`}>
            <span className="pipeline-dot" aria-hidden />
            <span className="pipeline-label">{stage}</span>
          </li>
        );
      })}
    </ol>
  );
}
