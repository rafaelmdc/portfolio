import type { Metadata } from "next";
import Script from "next/script";
import { Fraunces, Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import CommandPalette from "@/components/CommandPalette";

// Privacy-friendly analytics (self-hosted Umami). No-op until the env vars are
// set on the deployment, so it stays out of the way in dev/preview.
const UMAMI_SRC = process.env.NEXT_PUBLIC_UMAMI_SRC;
const UMAMI_WEBSITE_ID = process.env.NEXT_PUBLIC_UMAMI_WEBSITE_ID;

const fraunces = Fraunces({
  variable: "--font-fraunces",
  subsets: ["latin"],
  weight: ["400", "500", "600"],
  style: ["normal", "italic"],
});
const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
  weight: ["400", "500", "600"],
});
const jetbrains = JetBrains_Mono({
  variable: "--font-jetbrains",
  subsets: ["latin"],
  weight: ["400", "500"],
});

// Public site origin — used to make OG/sitemap URLs absolute (social scrapers
// need full URLs). Set SITE_URL in the frontend deployment; defaults to local.
const SITE_URL = process.env.SITE_URL || "http://localhost:8000";

const DESCRIPTION =
  "Bioinformatics student turning biological questions into reproducible code. Pipelines, genomics, data-driven analysis.";

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: "Rafael Correia — Bioinformatics",
  description: DESCRIPTION,
  openGraph: {
    type: "website",
    siteName: "Rafael Correia",
    title: "Rafael Correia — Bioinformatics",
    description: DESCRIPTION,
    url: "/",
  },
  twitter: {
    card: "summary_large_image",
    title: "Rafael Correia — Bioinformatics",
    description: DESCRIPTION,
  },
  alternates: {
    types: { "application/rss+xml": "/blog/feed.xml" },
  },
};

// Set the theme before paint to avoid a flash of the wrong palette.
const themeScript = `
(function () {
  try {
    var t = localStorage.getItem('theme');
    if (!t) t = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', t);
  } catch (e) {}
})();
`;

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: themeScript }} />
      </head>
      <body
        className={`${fraunces.variable} ${inter.variable} ${jetbrains.variable}`}
      >
        {children}
        <CommandPalette />
        {UMAMI_SRC && UMAMI_WEBSITE_ID && (
          <Script src={UMAMI_SRC} data-website-id={UMAMI_WEBSITE_ID} strategy="afterInteractive" />
        )}
      </body>
    </html>
  );
}
