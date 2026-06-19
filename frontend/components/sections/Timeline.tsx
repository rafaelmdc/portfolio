import type { SiteBundle, Education, Experience } from "@/lib/types";
import Eyebrow from "../Eyebrow";
import Reveal from "../Reveal";

function years(start: number | null, end: number | null) {
  return `${start ?? ""} — ${end ?? "Present"}`;
}

function Item({
  title,
  org,
  range,
  bullets,
}: {
  title: string;
  org: string;
  range: string;
  bullets?: string[];
}) {
  return (
    <div className="relative pb-[30px] last:pb-0 before:absolute before:left-[-25px] before:top-[6px] before:h-3 before:w-3 before:rounded-full before:border-2 before:border-primary before:bg-bg before:content-['']">
      <h4 className="m-0 mb-[3px] font-display text-[18px] font-medium">{title}</h4>
      <span className="mb-[7px] inline-block rounded-md bg-hl px-2 py-0.5 font-mono text-[11.5px] text-primary-ink">
        {range}
      </span>
      <p className="m-0 mb-[6px] text-[13.5px] text-muted">
        <em>{org}</em>
      </p>
      {bullets && bullets.length > 0 && (
        <ul className="mt-2 list-disc pl-[18px] text-[13.5px]">
          {bullets.map((b, i) => (
            <li key={i} className="mb-1">
              {b}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

function Stream({ children }: { children: React.ReactNode }) {
  return (
    <div className="relative pl-[26px] before:absolute before:bottom-[6px] before:left-[5px] before:top-[6px] before:w-0.5 before:bg-border before:content-['']">
      {children}
    </div>
  );
}

export default function Timeline({
  bundle,
  num,
  title,
}: {
  bundle: SiteBundle;
  num: number;
  title?: string;
}) {
  const exp: Experience[] = bundle.experience;
  const edu: Education[] = bundle.education;
  if (!exp.length && !edu.length) return null;

  return (
    <section id="timeline" className="border-b border-border py-24">
      <div className="mx-auto max-w-5xl px-7">
        <Reveal>
          <Eyebrow>§{num} — {title || "Timeline"}</Eyebrow>
        </Reveal>
        <div className="grid grid-cols-1 gap-[54px] md:grid-cols-2">
          {exp.length > 0 && (
            <Reveal>
              <p className="m-0 mb-[22px] font-mono text-[12px] tracking-[0.05em] text-muted">
                {"// research & experience"}
              </p>
              <Stream>
                {exp.map((x, i) => (
                  <Item
                    key={i}
                    title={x.role}
                    org={`${x.company}${x.location ? ` · ${x.location}` : ""}`}
                    range={years(x.start_year, x.end_year)}
                    bullets={x.bullets}
                  />
                ))}
              </Stream>
            </Reveal>
          )}
          {edu.length > 0 && (
            <Reveal>
              <p className="m-0 mb-[22px] font-mono text-[12px] tracking-[0.05em] text-muted">
                {"// education"}
              </p>
              <Stream>
                {edu.map((e, i) => (
                  <Item
                    key={i}
                    title={e.title}
                    org={`${e.institution}${e.location ? ` · ${e.location}` : ""}`}
                    range={years(e.start_year, e.end_year)}
                  />
                ))}
              </Stream>
            </Reveal>
          )}
        </div>
      </div>
    </section>
  );
}
