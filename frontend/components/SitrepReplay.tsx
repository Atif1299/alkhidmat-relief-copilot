"use client";

import { useEffect, useState } from "react";
import { PipelineStrip } from "@/components/PipelineStrip";
import type { AgentStep } from "@/lib/api";

const TRACE: AgentStep[] = [
  { agent: "Intake", action: "extract", detail: "lang=ur · Food packs, family of 5, Township" },
  { agent: "Triage", action: "classify", detail: "category=Food · priority=medium" },
  { agent: "Knowledge", action: "sop_retrieved", detail: "Food Relief SOP — Alkhidmat Lahore" },
  { agent: "Integrity", action: "risk_check", detail: "Clear · no duplicate on this phone" },
  { agent: "Matcher", action: "match", detail: "Lahore Kitchen · volunteer Ahmed Khan" },
  { agent: "Dispatch", action: "ticket_created", detail: "Ticket stamped for field follow-up" },
];

const TICKET = "AKD-SITREP-7AB355";
const STEP_MS = 1100;

function prefersReducedMotion(): boolean {
  if (typeof window === "undefined") return false;
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

export function SitrepReplay() {
  const [runId, setRunId] = useState(0);
  const [steps, setSteps] = useState<AgentStep[]>([]);
  const [done, setDone] = useState(false);

  useEffect(() => {
    if (prefersReducedMotion()) {
      setSteps(TRACE);
      setDone(true);
      return;
    }

    setSteps([]);
    setDone(false);
    let i = 0;
    const timer = window.setInterval(() => {
      i += 1;
      setSteps(TRACE.slice(0, i));
      if (i >= TRACE.length) {
        window.clearInterval(timer);
        setDone(true);
      }
    }, STEP_MS);

    return () => window.clearInterval(timer);
  }, [runId]);

  return (
    <aside className="sitrep-board" aria-label="Sitrep replay of the aid desk pipeline">
      <header className="sitrep-board-head">
        <p className="eyebrow">Lahore desk · Sitrep</p>
        <span className="sitrep-live">{done ? "Stamped" : "Running"}</span>
      </header>
      <p className="urdu sitrep-urdu" lang="ur">
        سیلاب کے بعد کھانے کی ضرورت ہے، ٹاؤن شپ لاہور
      </p>
      <p className="sitrep-en">Flood ke baad khane ki zaroorat hai, Township Lahore. Family of 5.</p>
      <PipelineStrip
        steps={steps}
        busy={!done}
        status={done ? "dispatched" : undefined}
      />
      <ol className="sitrep-trace" aria-live="polite">
        {steps.map((step) => (
          <li key={`${step.agent}-${step.action}`}>
            <strong>{step.agent}</strong>
            <span>{step.detail}</span>
          </li>
        ))}
      </ol>
      {done ? (
        <p className="sitrep-stamp-wrap">
          <span className="muted">Next action</span>
          <code className="ticket-stamp">{TICKET}</code>
        </p>
      ) : (
        <p className="muted sitrep-waiting">Agents verifying and matching…</p>
      )}
      <button
        type="button"
        className="btn ghost sitrep-replay-btn"
        onClick={() => setRunId((n) => n + 1)}
      >
        Replay sitrep
      </button>
    </aside>
  );
}
