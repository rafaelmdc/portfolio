import { ImageResponse } from "next/og";
import { getSiteBundle, assetUrl } from "@/lib/api";
import { OG_SIZE, OG_CONTENT_TYPE, C, SITE_DOMAIN, Wordmark, getOgFonts, clip } from "@/lib/og";

export const size = OG_SIZE;
export const contentType = OG_CONTENT_TYPE;
export const revalidate = 3600;
export const alt = "Rafael Correia — Bioinformatics";

export default async function Image() {
  const fonts = await getOgFonts();
  let bundle = null;
  try {
    bundle = await getSiteBundle();
  } catch {
    /* fall back to copy-only card */
  }
  const portrait = assetUrl(bundle?.images.home_profile?.url || bundle?.images.about_profile?.url);
  const name = bundle?.contact.full_name || "Rafael Correia";
  const role = bundle?.contact.role_title || "Bioinformatics · biology ∩ data";
  const tagline = clip(bundle?.copy.hero_headline || "I turn biological questions into reproducible code.", 90);

  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          background: C.bg,
          backgroundImage: `radial-gradient(900px 600px at 0% 0%, ${C.hl} 0%, transparent 55%)`,
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
            padding: "72px 56px",
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
            {role}
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: 22 }}>
            <div
              style={{
                display: "flex",
                fontFamily: "Fraunces",
                fontWeight: 600,
                fontSize: 88,
                lineHeight: 1.02,
                color: C.ink,
              }}
            >
              {name}
            </div>
            <div style={{ display: "flex", fontSize: 34, color: C.muted, lineHeight: 1.3, maxWidth: 620 }}>
              {tagline}
            </div>
          </div>
          <Wordmark />
        </div>
        <div style={{ display: "flex", alignItems: "center", paddingRight: 64 }}>
          {portrait ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img
              src={portrait}
              width={360}
              height={360}
              style={{
                width: 360,
                height: 360,
                objectFit: "cover",
                borderRadius: 36,
                border: `6px solid ${C.surface}`,
                boxShadow: "0 24px 60px -20px rgba(30,32,41,0.35)",
              }}
            />
          ) : (
            <div
              style={{
                width: 360,
                height: 360,
                borderRadius: 36,
                background: `linear-gradient(135deg, ${C.sky}, ${C.mint})`,
              }}
            />
          )}
        </div>
      </div>
    ),
    { ...size, fonts },
  );
}
