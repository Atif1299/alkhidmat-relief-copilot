"use client";

import { useState } from "react";
import Link from "next/link";
import { AgentTrace } from "@/components/AgentTrace";
import { PipelineStrip } from "@/components/PipelineStrip";
import { SopCitations } from "@/components/SopCitations";
import { chatStream, type AgentStep, type ChatResult } from "@/lib/api";

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

export default function RequestPage() {
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
        if (event === "hitl_required") {
          setResult((prev) => ({
            ...(prev || {}),
            ...(data as ChatResult),
            status: "pending_hitl",
          }));
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
      const raw = e instanceof Error ? e.message : "Request failed";
      if (raw.includes("422")) {
        setError("Please enter a valid aid request (1–4000 characters).");
      } else if (raw.includes("401")) {
        setError("Could not reach the aid desk (auth). Please try again in a moment.");
      } else if (raw.includes("Failed") || raw.includes("fetch")) {
        setError("Network error — check that the aid desk is online, then try again.");
      } else {
        setError(raw);
      }
    } finally {
      setBusy(false);
    }
  }

  const nextStep =
    result?.status === "dispatched" && result.ticket_id
      ? `Your ticket is ${result.ticket_id}. A volunteer will follow up.`
      : result?.status === "pending_hitl"
        ? "Your request is waiting for supervisor review. You will get a ticket after approval."
        : null;

  return (
    <div>
      <h1>Request aid</h1>
      <p className="muted">
        No account needed. Describe your need in Urdu or English — include area and a phone number
        if you can.
      </p>

      <div className="pipeline-wrap panel" style={{ marginTop: "1rem" }}>
        <p className="eyebrow" style={{ marginBottom: "0.65rem" }}>
          Live desk pipeline
        </p>
        <PipelineStrip steps={steps} busy={busy} status={result?.status} />
      </div>

      {result && nextStep && (
        <div
          className={`outcome-banner ${result.status === "dispatched" ? "ok" : "warn"}`}
          role="status"
        >
          <strong>
            {result.status === "dispatched" ? "Ticket created" : "Waiting for supervisor"}
          </strong>
          <p>{nextStep}</p>
          {result.ticket_id && <code className="ticket-id">{result.ticket_id}</code>}
        </div>
      )}

      <div className="grid-2" style={{ marginTop: "1rem" }}>
        <section className="panel">
          <h2>Your request</h2>
          <div className="chips">
            {SAMPLES.map((s) => (
              <button
                key={s.label}
                type="button"
                className="chip"
                onClick={() => setMessage(s.text)}
              >
                {s.label}
              </button>
            ))}
          </div>
          <label className="sr-only" htmlFor="aid-message">
            Aid request message
          </label>
          <textarea
            id="aid-message"
            rows={6}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
          />
          <div className="actions" style={{ marginTop: "0.75rem" }}>
            <button
              className="btn"
              type="button"
              disabled={busy || !message.trim()}
              onClick={submit}
            >
              {busy ? "Processing…" : "Submit request"}
            </button>
          </div>
          {error && <p className="error">{error}</p>}
          {result && (
            <div style={{ marginTop: "1rem" }}>
              <span
                className={`badge ${result.status === "dispatched"
                    ? "ok"
                    : result.status === "pending_hitl"
                      ? "warn"
                      : "neutral"
                  }`}
              >
                {result.status}
              </span>
              {result.notification && <p>{result.notification}</p>}
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

      <p className="muted" style={{ marginTop: "1.5rem" }}>
        Staff? <Link href="/login">Sign in to the ops desk</Link>
      </p>
    </div>
  );
}
