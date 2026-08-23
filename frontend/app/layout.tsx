import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Alkhidmat Relief Copilot",
  description: "Multi-agent NGO aid desk — Urdu/English relief tickets with HITL",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body style={{ margin: 0 }}>{children}</body>
    </html>
  );
}
