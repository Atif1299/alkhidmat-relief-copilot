export type DeskRole = "requester" | "desk" | "supervisor";

export const ROLE_KEY = "aiddesk_role";

/** Routes anyone can open without a JWT. */
export const PUBLIC_PATHS = ["/", "/request", "/status", "/login"] as const;

export function isPublicPath(pathname: string): boolean {
  if (PUBLIC_PATHS.includes(pathname as (typeof PUBLIC_PATHS)[number])) return true;
  return false;
}

export const ROLE_LINKS: Record<DeskRole, { href: string; label: string }[]> = {
  requester: [{ href: "/request", label: "Request aid" }],
  desk: [
    { href: "/tickets", label: "Tickets" },
    { href: "/dashboard", label: "Dashboard" },
    { href: "/chat", label: "Test intake" },
  ],
  supervisor: [
    { href: "/tickets", label: "Tickets" },
    { href: "/supervisor", label: "Supervisor" },
    { href: "/dashboard", label: "Dashboard" },
    { href: "/chat", label: "Test intake" },
  ],
};

export function staffHome(role: DeskRole): string {
  if (role === "requester") return "/request";
  return ROLE_LINKS[role][0]?.href || "/tickets";
}

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
  if (!ROLE_LINKS[role]) return false;
  if (isPublicPath(pathname)) return true;
  if (pathname.startsWith("/cases/")) {
    return role === "desk" || role === "supervisor";
  }
  const allowed = ROLE_LINKS[role].map((l) => l.href);
  return allowed.some((href) => pathname === href || pathname.startsWith(href + "/"));
}

export function navLinkActive(pathname: string, href: string): boolean {
  if (pathname === href) return true;
  if (href === "/tickets" && pathname.startsWith("/cases/")) return true;
  return false;
}
