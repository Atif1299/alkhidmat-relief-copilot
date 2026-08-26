export const API_URL =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") || "http://localhost:8000";

export type AgentStep = {
  agent: string;
  action: string;
  detail: string;
  ts_ms?: number;
};

export type SopHit = {
  title?: string;
  category?: string;
  excerpt?: string;
  score?: number;
  source_file?: string;
};

export type ChatResult = {
  case_id?: string;
  ticket_id?: string | null;
  status?: string;
  category?: string;
  priority?: string;
  language?: string;
  requires_hitl?: boolean;
  matched_resources?: unknown[];
  volunteer?: { name?: string; phone?: string } | null;
  agent_trace?: AgentStep[];
  notification?: string;
  sop_hits?: SopHit[];
  integrity?: {
    risk_score?: number;
    duplicate_flag?: boolean;
    reasons?: string[];
  };
};

export async function chatSync(message: string): Promise<ChatResult> {
  const res = await fetch(`${API_URL}/api/v1/chat/sync`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
  });
  if (!res.ok) throw new Error(`Chat failed: ${res.status}`);
  return res.json();
}

/** Stream SSE events from POST /api/v1/chat */
export async function chatStream(
  message: string,
  onEvent: (event: string, data: unknown) => void
): Promise<ChatResult | null> {
  const res = await fetch(`${API_URL}/api/v1/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "text/event-stream" },
    body: JSON.stringify({ message }),
  });
  if (!res.ok || !res.body) throw new Error(`Chat stream failed: ${res.status}`);

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let donePayload: ChatResult | null = null;
  let currentEvent = "message";

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const parts = buffer.split("\n");
    buffer = parts.pop() || "";
    for (const line of parts) {
      if (line.startsWith("event:")) {
        currentEvent = line.slice(6).trim();
      } else if (line.startsWith("data:")) {
        const raw = line.slice(5).trim();
        try {
          const data = JSON.parse(raw);
          onEvent(currentEvent, data);
          if (currentEvent === "done") donePayload = data as ChatResult;
        } catch {
          /* ignore partial */
        }
      }
    }
  }
  return donePayload;
}

export async function listCases(status?: string) {
  const q = status ? `?status=${encodeURIComponent(status)}` : "";
  const res = await fetch(`${API_URL}/api/v1/cases${q}`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to load cases");
  return res.json();
}

export async function getSupervisorQueue() {
  const res = await fetch(`${API_URL}/api/v1/supervisor/queue`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to load queue");
  return res.json();
}

export async function decideCase(caseId: string, decision: "approve" | "reject", note?: string) {
  const res = await fetch(`${API_URL}/api/v1/supervisor/${caseId}/decide`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ decision, note }),
  });
  if (!res.ok) throw new Error("Decision failed");
  return res.json();
}

export async function getMetrics() {
  const res = await fetch(`${API_URL}/api/v1/metrics`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to load metrics");
  return res.json();
}

export async function getCase(caseId: string) {
  const res = await fetch(`${API_URL}/api/v1/cases/${caseId}`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to load case");
  return res.json();
}

export async function getCaseTimeline(caseId: string) {
  const res = await fetch(`${API_URL}/api/v1/cases/${caseId}/timeline`, {
    cache: "no-store",
  });
  if (!res.ok) throw new Error("Failed to load timeline");
  return res.json();
}

export function caseExportPdfUrl(caseId: string) {
  return `${API_URL}/api/v1/cases/${caseId}/export.pdf`;
}
