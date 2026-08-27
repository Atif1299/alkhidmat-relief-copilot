"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { clearAuth, getAuthUser, getToken } from "@/lib/auth";
import {
  ROLE_LINKS,
  type DeskRole,
  roleMayAccess,
} from "@/lib/roles";

export function AppChrome({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const [role, setRole] = useState<DeskRole>("desk");
  const [email, setEmail] = useState<string | null>(null);
  const [ready, setReady] = useState(false);
  const isLogin = pathname === "/login";

  useEffect(() => {
    const token = getToken();
    const user = getAuthUser();
    if (!token || !user) {
      if (!isLogin) router.replace("/login");
      setReady(true);
      return;
    }
    setRole(user.role);
    setEmail(user.email);
    setReady(true);
  }, [pathname, isLogin, router]);

  useEffect(() => {
    if (!ready || isLogin) return;
    if (!roleMayAccess(role, pathname)) {
      router.replace(ROLE_LINKS[role][0]?.href || "/chat");
    }
  }, [ready, role, pathname, router, isLogin]);

  function logout() {
    clearAuth();
    router.replace("/login");
  }

  if (isLogin) {
    return <div className="shell"><div className="main">{children}</div></div>;
  }

  if (!ready) {
    return (
      <div className="shell">
        <div className="main">
          <p className="muted">Loading…</p>
        </div>
      </div>
    );
  }

  const links = ROLE_LINKS[role];

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
