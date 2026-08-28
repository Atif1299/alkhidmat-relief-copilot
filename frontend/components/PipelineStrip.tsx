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
  if (n.includes("dispatch") || n.includes("hitl") || n.includes("supervisor")) return "Dispatch";
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
  let activeIndex = -1;
  for (let i = 0; i < STAGES.length; i++) {
    if (done.has(STAGES[i])) activeIndex = i;
  }
  if (busy && activeIndex < STAGES.length - 1) {
    activeIndex = Math.min(activeIndex + 1, STAGES.length - 1);
  }
  if (status === "pending_hitl") {
    activeIndex = STAGES.indexOf("Integrity");
  }
  if (status === "dispatched") {
    activeIndex = STAGES.length - 1;
  }

  return (
    <ol className="pipeline-strip" aria-label="Agent pipeline">
      {STAGES.map((stage, i) => {
        let state = "pending";
        if (done.has(stage) || (status === "dispatched" && i <= STAGES.length - 1 && i <= activeIndex)) {
          state = "done";
        }
        if (busy && i === activeIndex) state = "active";
        if (!busy && status === "pending_hitl" && stage === "Integrity") state = "active";
        if (!busy && done.has(stage)) state = "done";
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
