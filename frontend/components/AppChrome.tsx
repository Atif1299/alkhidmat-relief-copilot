"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import {
  ROLE_LINKS,
  type DeskRole,
  readRole,
  roleMayAccess,
  writeRole,
} from "@/lib/roles";

export function AppChrome({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const [role, setRole] = useState<DeskRole>("desk");
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const current = readRole();
    setRole(current);
    setReady(true);
  }, []);

  useEffect(() => {
    if (!ready) return;
    if (!roleMayAccess(role, pathname)) {
      router.replace(ROLE_LINKS[role][0]?.href || "/chat");
    }
  }, [ready, role, pathname, router]);

  function onRoleChange(next: DeskRole) {
    writeRole(next);
    setRole(next);
    router.push(ROLE_LINKS[next][0]?.href || "/chat");
  }

  const links = ROLE_LINKS[role];

  return (
    <div className="shell">
      <header className="topbar">
        <div className="brand">
          Alkhidmat Relief Copilot
          <span>Aid Desk · Multi-Agent Ops · Tier B</span>
        </div>
        <div className="topbar-right">
          <label className="role-switch">
            <span>Role</span>
            <select
              value={role}
              onChange={(e) => onRoleChange(e.target.value as DeskRole)}
              aria-label="Demo role"
            >
              <option value="requester">Requester</option>
              <option value="desk">Desk</option>
              <option value="supervisor">Supervisor</option>
            </select>
          </label>
          <nav className="nav">
            {links.map((l) => (
              <Link key={l.href} href={l.href} className={pathname === l.href ? "active" : undefined}>
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
