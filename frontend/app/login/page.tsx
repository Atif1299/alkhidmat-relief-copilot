"use client";

import { FormEvent, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { login } from "@/lib/api";
import { setAuth } from "@/lib/auth";
import type { DeskRole } from "@/lib/roles";
import { staffHome } from "@/lib/roles";

const STAFF_ACCOUNTS = [
  {
    email: "desk@aiddesk.example",
    role: "Desk",
    hint: "Tickets, dashboard, PDF",
  },
  {
    email: "supervisor@aiddesk.example",
    role: "Supervisor",
    hint: "HITL approve / reject",
  },
];

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("desk@aiddesk.example");
  const [password, setPassword] = useState("AidDesk!2026");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const result = await login(email.trim(), password);
      const role = result.role as DeskRole;
      setAuth(result.access_token, {
        email: result.email,
        role,
        user_id: result.user_id,
      });
      router.replace(staffHome(role));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="login-wrap">
      <div className="panel login-card">
        <p className="eyebrow">Staff gate</p>
        <h1 style={{ marginTop: 0 }}>Sign in to the desk</h1>
        <p className="muted">
          Desk operators and supervisors only. Demo accounts fill email and password.
        </p>
        <div className="role-cards">
          {STAFF_ACCOUNTS.map((a) => (
            <button
              key={a.email}
              type="button"
              className={email === a.email ? "role-card active" : "role-card"}
              onClick={() => {
                setEmail(a.email);
                setPassword("AidDesk!2026");
              }}
            >
              <strong>{a.role}</strong>
              <span>{a.hint}</span>
            </button>
          ))}
        </div>
        <form onSubmit={onSubmit} className="stack" style={{ marginTop: "1rem" }}>
          <label>
            Email
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoComplete="username"
            />
          </label>
          <label>
            Password
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              autoComplete="current-password"
            />
          </label>
          {error ? <p className="error">{error}</p> : null}
          <button className="btn" type="submit" disabled={busy}>
            {busy ? "Signing in…" : "Sign in"}
          </button>
        </form>
        <p className="muted" style={{ marginTop: "1rem", fontSize: "0.8rem" }}>
          Demo password: <code className="ticket-stamp" style={{ fontSize: "0.78rem" }}>AidDesk!2026</code>
        </p>
        <p className="login-escape muted">
          Need help?{" "}
          <Link href="/request">Request aid — no account</Link>
          <br />
          <Link href="/">Back to home</Link>
        </p>
      </div>
    </div>
  );
}
