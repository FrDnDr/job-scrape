import type { Metadata } from "next";
import "./globals.css";
import "../styles/layout.css";
import "../styles/components/common.css";
import "../styles/components/metrics.css";
import "../styles/components/job-explorer.css";
import "../styles/components/resume-match.css";
import "../styles/components/market-intel.css";
import "../styles/components/learning-roadmap.css";

export const metadata: Metadata = {
  title: "Job Intelligence",
  description: "AI-powered job market and resume matching dashboard"
};

export default function RootLayout({
  children
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
