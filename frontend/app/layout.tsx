import type { Metadata } from "next";

import "./globals.css";

export const metadata: Metadata = {
  title: "AI Learn Coach",
  description: "Voice-first Hinglish learning coach for interview prep",
  manifest: "/manifest.webmanifest",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
