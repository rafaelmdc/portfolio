import type { SiteBundle, Publication } from "@/lib/types";
import Eyebrow from "../Eyebrow";
import Reveal from "../Reveal";

function Ref({ pub, index }: { pub: Publication; index: number }) {
  return (
    <div className="grid grid-cols-[42px_1fr] gap-[18px] border-t border-border py-[22px]">
      <div className="font-display text-[19px] text-muted">
        {String(index + 1).padStart(2, "0")}
      </div>
      <div>
        <p className="m-0 mb-1.5 font-display text-[19px] leading-[1.35]">
          {pub.title}
        </p>
        <p
          className="m-0 mb-[10px] text-[14px] text-muted [&_strong]:font-semibold [&_strong]:text-ink"
          dangerouslySetInnerHTML={{ __html: pub.authors_display }}
        />
        <div className="flex flex-wrap items-center gap-2">
          <span className="rounded-md border border-border px-[9px] py-[3px] font-mono text-[11.5px] text-muted">
            {pub.year}
          </span>
          {pub.venue && (
            <span className="rounded-md bg-sky px-[9px] py-[3px] font-mono text-[11.5px] text-chip-ink">
              {pub.venue}
            </span>
          )}
          {pub.link && (
            <a
              href={pub.link}
              target="_blank"
              rel="noopener noreferrer"
              className="rounded-md bg-hl px-[9px] py-[3px] font-mono text-[11.5px] text-primary-ink"
            >
              {pub.doi ? `[doi] ${pub.doi}` : "[link]"}
            </a>
          )}
          {pub.citation_count > 0 && (
            <span className="rounded-md bg-peach px-[9px] py-[3px] font-mono text-[11.5px] text-chip-ink">
              [cited by {pub.citation_count}]
            </span>
          )}
        </div>
      </div>
    </div>
  );
}

export default function Research({ bundle }: { bundle: SiteBundle }) {
  if (!bundle.has_research) return null;
  let i = 0;

  return (
    <section id="research" className="border-b border-border py-24">
      <div className="mx-auto max-w-5xl px-7">
        <Reveal>
          <Eyebrow>§5 — Research · publications</Eyebrow>
        </Reveal>
        {bundle.publications.groups.map((g) => (
          <Reveal key={g.label}>
            <h3 className="mb-1 mt-6 font-mono text-[12px] tracking-[0.05em] text-muted">
              // {g.label.toLowerCase()}
            </h3>
            {g.items.map((p) => (
              <Ref key={`${g.label}-${p.title}`} pub={p} index={i++} />
            ))}
          </Reveal>
        ))}
      </div>
    </section>
  );
}
