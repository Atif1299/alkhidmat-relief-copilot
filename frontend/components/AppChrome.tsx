"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { clearAuth, getAuthUser, getToken, type AuthUser } from "@/lib/auth";
import {
  ROLE_LINKS,
  type DeskRole,
  isPublicPath,
  navLinkActive,
  roleMayAccess,
  staffHome,
} from "@/lib/roles";

function isDeskRole(value: unknown): value is DeskRole {
  return value === "requester" || value === "desk" || value === "supervisor";
}

function readSession(): { token: string; user: AuthUser } | null {
  const token = getToken();
  const user = getAuthUser();
  if (!token || !user || !isDeskRole(user.role)) {
    if (token || user) clearAuth();
    return null;
  }
  return { token, user };
}

export function AppChrome({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const [role, setRole] = useState<DeskRole | null>(null);
  const [email, setEmail] = useState<string | null>(null);
  const [ready, setReady] = useState(false);
  const publicRoute = isPublicPath(pathname);

  useEffect(() => {
    const session = readSession();
    if (!session) {
      setRole(null);
      setEmail(null);
      setReady(true);
      if (!publicRoute) router.replace("/login");
      return;
    }
    setRole(session.user.role);
    setEmail(session.user.email);
    setReady(true);
    if (pathname === "/login") {
      router.replace(staffHome(session.user.role));
    }
  }, [pathname, publicRoute, router]);

  useEffect(() => {
    if (!ready || publicRoute || !role) return;
    if (!roleMayAccess(role, pathname)) {
      router.replace(staffHome(role));
    }
  }, [ready, role, pathname, router, publicRoute]);

  function logout() {
    clearAuth();
    setRole(null);
    setEmail(null);
    router.replace("/");
  }

  if (publicRoute) {
    return (
      <div className="shell">
        <header className="topbar public-topbar">
          <Link href="/" className="brand">
            Alkhidmat Relief Copilot
            <span>Aid Desk</span>
          </Link>
          <nav className="nav public-nav">
            <Link href="/request" className={pathname === "/request" ? "active" : undefined}>
              Request aid
            </Link>
            <Link href="/login" className={pathname === "/login" ? "active" : "nav-cta"}>
              Staff sign in
            </Link>
          </nav>
        </header>
        <div className={pathname === "/" ? "main main-wide" : "main"}>{children}</div>
      </div>
    );
  }

  if (!ready || !role) {
    return (
      <div className="shell">
        <div className="main">
          <p className="muted">Loading…</p>
        </div>
      </div>
    );
  }

  const links = ROLE_LINKS[role] ?? ROLE_LINKS.desk;

  return (
    <div className="shell">
      <header className="topbar">
        <Link href={staffHome(role)} className="brand">
          Alkhidmat Relief Copilot
          <span>Aid Desk</span>
        </Link>
        <div className="topbar-right">
          <span className="role-switch">
            <span>{email}</span>
            <strong style={{ marginLeft: 8 }}>{role}</strong>
          </span>
          <button type="button" className="btn secondary" onClick={logout}>
            Log out
          </button>
          <nav className="nav">
            {links.map((l) => (
              <Link
                key={l.href}
                href={l.href}
                className={navLinkActive(pathname, l.href) ? "active" : undefined}
              >
                {l.label}
              </Link>
            ))}
          </nav>
        </div>
      </header>
      <div className="main">{children}</div>
    </div>
  );
}
