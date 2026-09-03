"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { BrandMark } from "@/components/BrandMark";
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

function BrandLockup({ href }: { href: string }) {
  return (
    <Link href={href} className="brand">
      <BrandMark />
      <span className="brand-text">
        <span className="brand-name">Alkhidmat Relief Copilot</span>
        <span className="brand-sub">
          <span lang="ur" className="urdu">
            امداد ڈیسک
          </span>
          <span aria-hidden="true"> · </span>
          Aid Desk
        </span>
      </span>
    </Link>
  );
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
          <BrandLockup href="/" />
          <nav className="nav public-nav">
            <Link
              href="/request"
              className={pathname === "/request" ? "active nav-cta" : "nav-cta"}
            >
              Request aid
            </Link>
            <Link href="/login" className={pathname === "/login" ? "active" : undefined}>
              Staff sign in
            </Link>
          </nav>
        </header>
        <div className="main">{children}</div>
      </div>
    );
  }

  if (!ready || !role) {
    return (
      <div className="shell">
        <div className="main">
          <p className="muted">Loading desk…</p>
        </div>
      </div>
    );
  }

  const links = ROLE_LINKS[role] ?? ROLE_LINKS.desk;

  return (
    <div className="shell">
      <header className="topbar">
        <BrandLockup href={staffHome(role)} />
        <div className="topbar-right">
          <span className="role-switch">
            <span className="topbar-email">{email}</span>
            <span className="role-pill">{role}</span>
          </span>
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
          <button type="button" className="btn topbar-logout" onClick={logout}>
            Log out
          </button>
        </div>
      </header>
      <div className="main">{children}</div>
    </div>
  );
}
