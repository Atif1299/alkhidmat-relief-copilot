import type { Metadata } from "next";
import { AppChrome } from "@/components/AppChrome";
import "./globals.css";

export const metadata: Metadata = {
  title: "Alkhidmat Relief Copilot",
  description: "Multi-agent NGO aid desk — Urdu/English relief tickets with HITL",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <AppChrome>{children}</AppChrome>
      </body>
    </html>
  );
}
