"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { clearAuth, getAuthUser, getToken, type AuthUser } from "@/lib/auth";
import {
  ROLE_LINKS,
  type DeskRole,
  roleMayAccess,
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
  const isLogin = pathname === "/login";

  useEffect(() => {
    const session = readSession();
    if (!session) {
      setRole(null);
      setEmail(null);
      setReady(true);
      if (!isLogin) router.replace("/login");
      return;
    }
    setRole(session.user.role);
    setEmail(session.user.email);
    setReady(true);
    if (isLogin) {
      router.replace(ROLE_LINKS[session.user.role][0]?.href || "/chat");
    }
  }, [pathname, isLogin, router]);

  useEffect(() => {
    if (!ready || isLogin || !role) return;
    if (!roleMayAccess(role, pathname)) {
      router.replace(ROLE_LINKS[role][0]?.href || "/chat");
    }
  }, [ready, role, pathname, router, isLogin]);

  function logout() {
    clearAuth();
    setRole(null);
    setEmail(null);
    router.replace("/login");
  }

  if (isLogin) {
    return (
      <div className="shell">
        <div className="main">{children}</div>
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
        <div className="brand">
          Alkhidmat Relief Copilot
          <span>Aid Desk · Multi-Agent Ops · Tier 3</span>
        </div>
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
                className={pathname === l.href ? "active" : undefined}
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
