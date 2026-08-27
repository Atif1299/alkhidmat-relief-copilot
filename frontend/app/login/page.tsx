"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { login } from "@/lib/api";
import { setAuth } from "@/lib/auth";
import type { DeskRole } from "@/lib/roles";
import { ROLE_LINKS } from "@/lib/roles";

const DEMO_ACCOUNTS = [
  { email: "citizen@aiddesk.example", role: "Requester" },
  { email: "desk@aiddesk.example", role: "Desk" },
  { email: "supervisor@aiddesk.example", role: "Supervisor" },
];

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("supervisor@aiddesk.example");
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
      router.replace(ROLE_LINKS[role]?.[0]?.href || "/chat");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="panel" style={{ maxWidth: 440, margin: "3rem auto" }}>
      <h1 style={{ marginTop: 0 }}>Sign in</h1>
      <p className="muted">
        Tier 3 JWT roles — use a seeded demo account (password{" "}
        <code>AidDesk!2026</code>).
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
        {DEMO_ACCOUNTS.map((a) => (
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
    </div>
  );
}
