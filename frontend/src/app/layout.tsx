import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "CyberExplain AI — Multi-Agent Cybersecurity Assessment",
  description:
    "Explainability and transparency in multi-agent cybersecurity decision-making. Interactive agent decision graph with verification and correction.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en" className="dark">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link
          rel="preconnect"
          href="https://fonts.gstatic.com"
          crossOrigin="anonymous"
        />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="antialiased">{children}</body>
    </html>
  );
}
