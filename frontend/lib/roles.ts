export type DeskRole = "requester" | "desk" | "supervisor";

export const ROLE_KEY = "aiddesk_role";

export const ROLE_LINKS: Record<DeskRole, { href: string; label: string }[]> = {
  requester: [{ href: "/chat", label: "Chat" }],
  desk: [
    { href: "/chat", label: "Chat" },
    { href: "/tickets", label: "Tickets" },
    { href: "/dashboard", label: "Dashboard" },
  ],
  supervisor: [
    { href: "/chat", label: "Chat" },
    { href: "/tickets", label: "Tickets" },
    { href: "/supervisor", label: "Supervisor" },
    { href: "/dashboard", label: "Dashboard" },
  ],
};

export function readRole(): DeskRole {
  if (typeof window === "undefined") return "desk";
  const value = window.localStorage.getItem(ROLE_KEY);
  if (value === "requester" || value === "desk" || value === "supervisor") return value;
  return "desk";
}

export function writeRole(role: DeskRole) {
  window.localStorage.setItem(ROLE_KEY, role);
}

export function roleMayAccess(role: DeskRole, pathname: string): boolean {
  if (pathname.startsWith("/cases/")) {
    return role === "desk" || role === "supervisor";
  }
  const allowed = ROLE_LINKS[role].map((l) => l.href);
  if (pathname === "/" || pathname === "") return true;
  return allowed.some((href) => pathname === href || pathname.startsWith(href + "/"));
}
