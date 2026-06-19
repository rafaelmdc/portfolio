import React from "react";

// Shared building blocks for the dynamic OG images (next/og ImageResponse).
// ImageResponse only supports flexbox + a CSS subset, so everything here is
// inline-styled and every multi-child container is display:flex.

export const OG_SIZE = { width: 1200, height: 630 };
export const OG_CONTENT_TYPE = "image/png";

// Light-palette brand tokens (mirrors app/globals.css :root).
export const C = {
  bg: "#f7f5fb",
  surface: "#ffffff",
  ink: "#1e2029",
  muted: "#6e6e7b",
  border: "#e7e3f0",
  primary: "#6a4fbf",
  hl: "#e0d6f7",
  mint: "#cfeee0",
  sky: "#d3e7f8",
};

export const SITE_DOMAIN = "rafael.duarte-correia.pt";

/**
 * Load a Google font as an ArrayBuffer for ImageResponse. Best-effort: parses
 * the CSS for the woff2 URL and fetches it. Returns null on any failure so the
 * card still renders with the system font instead of breaking.
 */
export async function loadGoogleFont(
  family: string,
  weight: number,
  text?: string,
): Promise<ArrayBuffer | null> {
  try {
    const params = new URLSearchParams({
      family: `${family}:wght@${weight}`,
    });
    if (text) params.set("text", text);
    const cssUrl = `https://fonts.googleapis.com/css2?${params}`;
    const css = await fetch(cssUrl, {
      headers: {
        // Desktop UA → Google serves woff2 with a stable url() we can parse.
        "User-Agent":
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
      },
    }).then((r) => r.text());
    const url = css.match(/src:\s*url\(([^)]+)\)\s*format\('(?:woff2|truetype)'\)/)?.[1];
    if (!url) return null;
    const res = await fetch(url);
    if (!res.ok) return null;
    return await res.arrayBuffer();
  } catch {
    return null;
  }
}

type OgFont = {
  name: string;
  data: ArrayBuffer;
  weight: 400 | 600;
  style: "normal";
};

let fontsPromise: Promise<OgFont[]> | null = null;

/** Brand fonts for ImageResponse, loaded once and reused. Degrades to []. */
export function getOgFonts(): Promise<OgFont[]> {
  if (!fontsPromise) {
    fontsPromise = Promise.all([
      loadGoogleFont("Fraunces", 600),
      loadGoogleFont("Inter", 400),
      loadGoogleFont("Inter", 600),
    ]).then(([fraunces, inter, interBold]) => {
      const fonts: OgFont[] = [];
      if (fraunces) fonts.push({ name: "Fraunces", data: fraunces, weight: 600, style: "normal" });
      if (inter) fonts.push({ name: "Inter", data: inter, weight: 400, style: "normal" });
      if (interBold) fonts.push({ name: "Inter", data: interBold, weight: 600, style: "normal" });
      return fonts;
    });
  }
  return fontsPromise;
}

/** Truncate a string to n chars with an ellipsis. */
export function clip(s: string, n: number): string {
  const t = (s || "").trim();
  return t.length > n ? t.slice(0, n - 1).trimEnd() + "…" : t;
}

/** Decorative double-helix dot column for the right edge of a card. */
function HelixDots() {
  const rows = Array.from({ length: 12 });
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
      {rows.map((_, i) => {
        const phase = Math.sin((i / 11) * Math.PI * 2);
        const offset = Math.round(phase * 26);
        return (
          <div
            key={i}
            style={{
              display: "flex",
              alignItems: "center",
              gap: 10,
              transform: `translateX(${offset}px)`,
            }}
          >
            <div
              style={{ width: 14, height: 14, borderRadius: 14, background: C.primary, opacity: 0.55 }}
            />
            <div style={{ width: 34, height: 2, background: C.border }} />
            <div
              style={{ width: 14, height: 14, borderRadius: 14, background: C.mint, opacity: 0.9 }}
            />
          </div>
        );
      })}
    </div>
  );
}

/** Wordmark footer shared by blog/project cards. */
export function Wordmark() {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 14, color: C.muted, fontSize: 26 }}>
      <div style={{ width: 12, height: 12, borderRadius: 12, background: C.primary }} />
      <span style={{ color: C.ink, fontWeight: 600 }}>Rafael Correia</span>
      <span>·</span>
      <span>{SITE_DOMAIN}</span>
    </div>
  );
}

/**
 * Standard card frame for blog/project: eyebrow → title → wordmark, with the
 * helix motif on the right and a primary accent bar on the left.
 */
export function CardFrame({
  eyebrow,
  title,
  subtitle,
}: {
  eyebrow: string;
  title: string;
  subtitle?: string;
}) {
  return (
    <div
      style={{
        width: "100%",
        height: "100%",
        display: "flex",
        background: C.bg,
        backgroundImage: `radial-gradient(900px 500px at 12% 0%, ${C.hl} 0%, transparent 55%)`,
        fontFamily: "Inter",
      }}
    >
      <div style={{ width: 14, height: "100%", background: C.primary }} />
      <div
        style={{
          flex: 1,
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          padding: "72px 64px",
        }}
      >
        <div
          style={{
            display: "flex",
            textTransform: "uppercase",
            letterSpacing: 4,
            fontSize: 24,
            color: C.primary,
            fontWeight: 600,
          }}
        >
          {eyebrow}
        </div>
        <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>
          <div
            style={{
              display: "flex",
              fontFamily: "Fraunces",
              fontWeight: 600,
              fontSize: title.length > 48 ? 64 : 80,
              lineHeight: 1.05,
              color: C.ink,
            }}
          >
            {title}
          </div>
          {subtitle ? (
            <div style={{ display: "flex", fontSize: 30, color: C.muted, lineHeight: 1.35 }}>
              {subtitle}
            </div>
          ) : null}
        </div>
        <Wordmark />
      </div>
      <div
        style={{
          width: 220,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <HelixDots />
      </div>
    </div>
  );
}
