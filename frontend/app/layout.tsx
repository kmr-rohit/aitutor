import type { Metadata, Viewport } from "next";
import Script from "next/script";

import "./globals.css";

export const metadata: Metadata = {
  title: "AI Tutor Voice Coach",
  description: "Voice-first Hinglish learning coach for interview prep",
  manifest: "/manifest.webmanifest",
};

export const viewport: Viewport = {
  themeColor: "#0d1713",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        {children}
        <Script id="pwa-sw-register" strategy="afterInteractive">
          {`
            if ('serviceWorker' in navigator) {
              window.addEventListener('load', function () {
                navigator.serviceWorker.register('/sw.js').catch(function () {});
              });
            }
          `}
        </Script>
      </body>
    </html>
  );
}
