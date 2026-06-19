import type { Metadata } from "next";
import { Fraunces, Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import CommandPalette from "@/components/CommandPalette";

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
      </body>
    </html>
  );
}
