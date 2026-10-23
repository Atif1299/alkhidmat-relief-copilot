/** Shared display helpers for staff pages (status labels, priority tones, times). */

export const STATUS_META: Record<string, { label: string; tone: string }> = {
  dispatched: { label: "Dispatched", tone: "ok" },
  pending_hitl: { label: "Waiting for supervisor", tone: "warn" },
  processing: { label: "Received", tone: "neutral" },
  open: { label: "Received", tone: "neutral" },
  rejected: { label: "Not approved", tone: "danger" },
  closed: { label: "Closed", tone: "neutral" },
};

export const STATUS_ORDER = ["dispatched", "pending_hitl", "processing", "open", "rejected", "closed"];

export function statusMeta(status: string) {
  return STATUS_META[status] ?? { label: status, tone: "neutral" };
}

export function priorityTone(priority?: string | null) {
  if (priority === "critical") return "danger";
  if (priority === "high") return "warn";
  return "neutral";
}

/** API timestamps are naive UTC. */
export function parseUtc(value?: string | null): Date | null {
  if (!value) return null;
  const hasZone = /[zZ]|[+-]\d\d:?\d\d$/.test(value);
  const d = new Date(hasZone ? value : `${value}Z`);
  return Number.isNaN(d.getTime()) ? null : d;
}

export function timeAgo(value?: string | null, now = Date.now()): string {
  const d = parseUtc(value);
  if (!d) return "—";
  const s = Math.max(0, Math.round((now - d.getTime()) / 1000));
  if (s < 60) return "just now";
  const m = Math.round(s / 60);
  if (m < 60) return `${m} min ago`;
  const h = Math.round(m / 60);
  if (h < 24) return `${h} h ago`;
  return d.toLocaleDateString(undefined, { day: "numeric", month: "short" });
}

/** "12 min", "3 h", "2 d" — how long something has been waiting. */
export function waitingFor(value?: string | null, now = Date.now()): string {
  const d = parseUtc(value);
  if (!d) return "—";
  const m = Math.max(0, Math.round((now - d.getTime()) / 60000));
  if (m < 60) return `${m} min`;
  const h = Math.round(m / 60);
  if (h < 48) return `${h} h`;
  return `${Math.round(h / 24)} d`;
}

export function seconds(ms?: number | null): string {
  if (ms == null) return "—";
  return `${(ms / 1000).toFixed(1)}s`;
}
