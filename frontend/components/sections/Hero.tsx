import type { SiteBundle } from "@/lib/types";

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

  return (
    <section className="relative mx-auto max-w-5xl px-7 pb-[92px] pt-[104px]">
      <div
        className="rise mb-[18px] font-mono text-[12px] tracking-[0.06em] text-primary"
        style={{ animationDelay: "0.18s" }}
      >
        §0 — {eyebrow}
      </div>
      <h1
        className="rise m-0 mb-[26px] max-w-[16ch] font-display text-[clamp(40px,6.4vw,80px)] font-medium leading-[1.04]"
        style={{ animationDelay: "0.31s" }}
      >
        {headlineEl}
      </h1>
      <p
        className="rise m-0 mb-[34px] max-w-[56ch] text-[clamp(17px,2vw,20px)] text-muted"
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
    </section>
  );
}
