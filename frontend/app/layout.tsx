import Link from "next/link";
import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Alkhidmat Relief Copilot",
  description: "Multi-agent NGO aid desk — Urdu/English relief tickets with HITL",
};

const links = [
  { href: "/chat", label: "Chat" },
  { href: "/tickets", label: "Tickets" },
  { href: "/supervisor", label: "Supervisor" },
  { href: "/dashboard", label: "Dashboard" },
];

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="shell">
          <header className="topbar">
            <div className="brand">
              Alkhidmat Relief Copilot
              <span>Aid Desk · Multi-Agent Ops</span>
            </div>
            <nav className="nav">
              {links.map((l) => (
                <Link key={l.href} href={l.href}>
                  {l.label}
                </Link>
              ))}
            </nav>
          </header>
          <div className="main">{children}</div>
        </div>
      </body>
    </html>
  );
}
