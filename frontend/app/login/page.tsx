"use client";

import { FormEvent, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { login } from "@/lib/api";
import { setAuth } from "@/lib/auth";
import type { DeskRole } from "@/lib/roles";
import { staffHome } from "@/lib/roles";

const STAFF_ACCOUNTS = [
  { email: "desk@aiddesk.example", role: "Desk" },
  { email: "supervisor@aiddesk.example", role: "Supervisor" },
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
        <h1 style={{ marginTop: 0 }}>Staff sign in</h1>
        <p className="muted">
          For desk operators and supervisors. Citizens should{" "}
          <Link href="/request">request aid</Link> without an account.
        </p>
        <form onSubmit={onSubmit} className="stack">
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
        <div className="chip-row" style={{ marginTop: "1.25rem" }}>
          {STAFF_ACCOUNTS.map((a) => (
            <button
              key={a.email}
              type="button"
              className="chip"
              onClick={() => {
                setEmail(a.email);
                setPassword("AidDesk!2026");
              }}
            >
              {a.role}
            </button>
          ))}
        </div>
        <p className="muted" style={{ marginTop: "1rem", fontSize: "0.8rem" }}>
          Demo password: <code>AidDesk!2026</code>
        </p>
        <p className="muted" style={{ marginTop: "0.75rem" }}>
          <Link href="/">← Back to home</Link>
        </p>
      </div>
    </div>
  );
}
