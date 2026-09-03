/**
 * API base URL.
 * - Unset / missing in local Next: http://localhost:8000
 * - Empty string (Docker build ARG): same-origin relative paths via nginx (/api/...)
 * - Explicit URL: that host
 */
import { authHeaders, clearAuth, getToken } from "./auth";

function resolveApiUrl(): string {
  const raw = process.env.NEXT_PUBLIC_API_URL;
  if (raw === "") {
    return "";
  }
  if (raw == null || raw === undefined) {
    return "http://localhost:8000";
  }
  return raw.replace(/\/$/, "");
}

export const API_URL = resolveApiUrl();

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
  retrieval_mode?: string;
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

export type LoginResult = {
  access_token: string;
  token_type: string;
  role: string;
  email: string;
  user_id: string;
};

export async function login(email: string, password: string): Promise<LoginResult> {
  const res = await fetch(`${API_URL}/api/v1/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(detail || `Login failed: ${res.status}`);
  }
  return res.json();
}

export async function fetchMe() {
  const res = await fetch(`${API_URL}/api/v1/auth/me`, {
    headers: authHeaders(),
    cache: "no-store",
  });
  if (!res.ok) throw new Error("Not authenticated");
  return res.json();
}

export async function chatSync(message: string): Promise<ChatResult> {
  const res = await fetch(`${API_URL}/api/v1/chat/sync`, {
    method: "POST",
    headers: authHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify({ message }),
  });
  if (!res.ok) throw new Error(`Chat failed: ${res.status}`);
  return res.json();
}

const CHAT_STREAM_HEADERS = {
  "Content-Type": "application/json",
  Accept: "text/event-stream",
};

/** Stream SSE events from POST /api/v1/chat */
export async function chatStream(
  message: string,
  onEvent: (event: string, data: unknown) => void,
  options?: { anonymous?: boolean }
): Promise<ChatResult | null> {
  const skipAuth = options?.anonymous === true;
  let res = await fetch(`${API_URL}/api/v1/chat`, {
    method: "POST",
    headers: skipAuth ? CHAT_STREAM_HEADERS : authHeaders(CHAT_STREAM_HEADERS),
    body: JSON.stringify({ message }),
  });
  // Public intake allows guests. A leftover / expired staff token must not block it.
  if (res.status === 401 && getToken()) {
    clearAuth();
    res = await fetch(`${API_URL}/api/v1/chat`, {
      method: "POST",
      headers: CHAT_STREAM_HEADERS,
      body: JSON.stringify({ message }),
    });
  }
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
  const res = await fetch(`${API_URL}/api/v1/cases${q}`, {
    headers: authHeaders(),
    cache: "no-store",
  });
  if (!res.ok) throw new Error("Failed to load cases");
  return res.json();
}

export async function getSupervisorQueue() {
  const res = await fetch(`${API_URL}/api/v1/supervisor/queue`, {
    headers: authHeaders(),
    cache: "no-store",
  });
  if (!res.ok) throw new Error("Failed to load queue");
  return res.json();
}

export async function decideCase(caseId: string, decision: "approve" | "reject", note?: string) {
  const res = await fetch(`${API_URL}/api/v1/supervisor/${caseId}/decide`, {
    method: "POST",
    headers: authHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify({ decision, note }),
  });
  if (!res.ok) throw new Error("Decision failed");
  return res.json();
}

export async function getMetrics() {
  const res = await fetch(`${API_URL}/api/v1/metrics`, {
    headers: authHeaders(),
    cache: "no-store",
  });
  if (!res.ok) throw new Error("Failed to load metrics");
  return res.json();
}

export async function getCase(caseId: string) {
  const res = await fetch(`${API_URL}/api/v1/cases/${caseId}`, {
    headers: authHeaders(),
    cache: "no-store",
  });
  if (!res.ok) throw new Error("Failed to load case");
  return res.json();
}

export async function getCaseTimeline(caseId: string) {
  const res = await fetch(`${API_URL}/api/v1/cases/${caseId}/timeline`, {
    headers: authHeaders(),
    cache: "no-store",
  });
  if (!res.ok) throw new Error("Failed to load timeline");
  return res.json();
}

export function caseExportPdfUrl(caseId: string) {
  return `${API_URL}/api/v1/cases/${caseId}/export.pdf`;
}

/** Download PDF with Bearer token (cannot use plain <a href>). */
export async function downloadCasePdf(caseId: string, filename?: string) {
  const res = await fetch(caseExportPdfUrl(caseId), {
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error("PDF export failed");
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename || `${caseId}.pdf`;
  a.click();
  URL.revokeObjectURL(url);
}

export function requireTokenOrThrow() {
  if (!getToken()) throw new Error("Not logged in");
}
