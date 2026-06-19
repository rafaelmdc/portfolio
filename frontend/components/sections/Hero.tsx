import type { SiteBundle } from "@/lib/types";
import { mediaUrl } from "@/lib/api";
import HeroBackground from "../HeroBackground";

export default function Hero({ bundle }: { bundle: SiteBundle }) {
  const { copy } = bundle;
  const lead =
    copy.about_lead ||
    "I build pipelines that turn messy biology into structured, data-driven insight.";
  const name = bundle.contact.full_name || "Rafael Correia";

  const eyebrow = copy.hero_eyebrow || "MSc Bioinformatics · biology ∩ data";
  const headline =
    copy.hero_headline || "I turn biological questions into reproducible code.";
  // Highlight the configured phrase within the headline, if present.
  const hl = copy.hero_highlight;
  const idx = hl ? headline.indexOf(hl) : -1;
  const headlineEl =
    idx >= 0 ? (
      <>
        {headline.slice(0, idx)}
        <span className="hl-sweep">{headline.slice(idx, idx + hl.length)}</span>
        {headline.slice(idx + hl.length)}
      </>
    ) : (
      headline
    );

  // The profile image moved here from the About section.
  const img = bundle.images.about_profile || bundle.images.home_profile;

  return (
    <section className="relative isolate min-h-[calc(100svh-62px)] w-full overflow-hidden">
      {/* Full-bleed animated backdrop (spans the viewport width). */}
      <HeroBackground />
      {/* Content stays centered/constrained, the same width as the rest. */}
      <div className="relative z-10 mx-auto flex min-h-[calc(100svh-62px)] max-w-7xl items-center px-7 py-16 lg:px-12">
        <div className="grid w-full grid-cols-1 items-center gap-12 lg:grid-cols-[1.05fr_0.95fr] lg:gap-16">
        {/* Left: intro copy */}
        <div>
          <div
            className="rise mb-[18px] font-mono text-[12px] tracking-[0.06em] text-primary"
            style={{ animationDelay: "0.18s" }}
          >
            §0 — {eyebrow}
          </div>
          <h1
            className="rise m-0 mb-[26px] max-w-[15ch] font-display text-[clamp(38px,5.2vw,68px)] font-medium leading-[1.04]"
            style={{ animationDelay: "0.31s" }}
          >
            {headlineEl}
          </h1>
          <p
            className="rise m-0 mb-[34px] max-w-[52ch] text-[clamp(17px,2vw,20px)] text-muted"
            style={{ animationDelay: "0.44s" }}
          >
            Hi, I&apos;m <strong className="font-medium text-ink">{name}</strong>. {lead}
          </p>
          <div
            className="rise flex flex-wrap gap-[14px]"
            style={{ animationDelay: "0.57s" }}
          >
            <a
              href="#work"
              className="inline-flex items-center gap-[9px] rounded-[11px] border border-primary bg-primary px-[18px] py-3 font-mono text-[13px] text-[var(--on-primary)] transition hover:-translate-y-0.5"
            >
              ↗ {copy.hero_cta_primary || "View selected work"}
            </a>
            <a
              href="#timeline"
              className="inline-flex items-center gap-[9px] rounded-[11px] border border-border bg-surface px-[18px] py-3 font-mono text-[13px] transition hover:-translate-y-0.5 hover:shadow-[var(--shadow)]"
            >
              ↓ {copy.hero_cta_secondary || "Timeline & CV"}
            </a>
          </div>
        </div>

        {/* Right: big square portrait */}
        {img && (
          <div className="rise" style={{ animationDelay: "0.5s" }}>
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={mediaUrl(img.url)}
              alt={img.alt}
              className="aspect-square w-full rounded-3xl border border-border object-cover shadow-[var(--shadow)]"
            />
          </div>
        )}
        </div>
      </div>
    </section>
  );
}
