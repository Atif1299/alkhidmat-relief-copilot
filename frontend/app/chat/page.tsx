"use client";

import { useState } from "react";
import { AgentTrace } from "@/components/AgentTrace";
import { SopCitations } from "@/components/SopCitations";
import { chatStream, type AgentStep, type ChatResult } from "@/lib/api";
import Link from "next/link";

const SAMPLES = [
  {
    label: "Urdu · Food",
    text: "Flood ke baad khane ki zaroorat hai, Township Lahore, family of 5. Phone 03017654321",
  },
  {
    label: "EN · Duplicate",
    text: "Need food packs again for my family in Township Lahore. Phone 03001234567",
  },
  {
    label: "Critical · Medical",
    text: "Chest pain, need ambulance, Johar Town. Phone 03018887766",
  },
];

export default function ChatPage() {
  const [message, setMessage] = useState(SAMPLES[0].text);
  const [steps, setSteps] = useState<AgentStep[]>([]);
  const [result, setResult] = useState<ChatResult | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function submit() {
    setBusy(true);
    setError(null);
    setSteps([]);
    setResult(null);
    try {
      const done = await chatStream(message, (event, data) => {
        if (event === "agent_step") {
          setSteps((prev) => [...prev, data as AgentStep]);
        }
        if (event === "done") {
          setResult(data as ChatResult);
          if ((data as ChatResult).agent_trace?.length) {
            setSteps((data as ChatResult).agent_trace || []);
          }
        }
      });
      if (done) setResult(done);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Request failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div>
      <h1>Citizen intake</h1>
      <p className="muted">
        Submit Urdu or English aid requests. Watch Intake → Triage → Knowledge → Integrity → Matcher
        → Dispatch run live.
      </p>

      <div className="grid-2" style={{ marginTop: "1rem" }}>
        <section className="panel">
          <h2>Request</h2>
          <div className="chips">
            {SAMPLES.map((s) => (
              <button key={s.label} type="button" className="chip" onClick={() => setMessage(s.text)}>
                {s.label}
              </button>
            ))}
          </div>
          <textarea rows={6} value={message} onChange={(e) => setMessage(e.target.value)} />
          <div className="actions" style={{ marginTop: "0.75rem" }}>
            <button className="btn" type="button" disabled={busy || !message.trim()} onClick={submit}>
              {busy ? "Agents running…" : "Run desk pipeline"}
            </button>
          </div>
          {error && <p style={{ color: "var(--danger)" }}>{error}</p>}
          {result && (
            <div style={{ marginTop: "1rem" }}>
              <span
                className={`badge ${
                  result.status === "dispatched"
                    ? "ok"
                    : result.status === "pending_hitl"
                      ? "warn"
                      : "neutral"
                }`}
              >
                {result.status}
              </span>{" "}
              {result.ticket_id && <strong>{result.ticket_id}</strong>}
              <p className="muted">
                {result.category} · {result.priority} · {result.language}
                {result.integrity?.duplicate_flag ? " · duplicate flagged" : ""}
              </p>
              {result.notification && <p>{result.notification}</p>}
              {result.case_id && (
                <p>
                  <Link href={`/cases/${result.case_id}`}>Open case timeline &amp; PDF →</Link>
                </p>
              )}
              {result.status === "pending_hitl" && (
                <p>
                  Waiting for supervisor — open <a href="/supervisor">Supervisor</a>.
                </p>
              )}
              <h3 style={{ marginTop: "1rem" }}>SOP citations</h3>
              <SopCitations hits={result.sop_hits} />
            </div>
          )}
        </section>

        <aside className="panel">
          <h2>Agent trace</h2>
          <AgentTrace steps={steps} />
        </aside>
      </div>
    </div>
  );
}
