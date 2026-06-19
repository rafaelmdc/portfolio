import type { SiteBundle } from "@/lib/types";
import Eyebrow from "../Eyebrow";
import Reveal from "../Reveal";

const BIO = /biolog|genetic|ecolog|evolu|physiolog|microbio|organism|taxonom|molecular|anatom/i;

export default function Skills({ bundle }: { bundle: SiteBundle }) {
  const skills = bundle.skills;
  if (!skills.length) return null;

  return (
    <section id="skills" className="border-b border-border py-24">
      <div className="mx-auto max-w-5xl px-7">
        <Reveal>
          <Eyebrow centered>§2 — {bundle.copy.skills_title || "Skills"}</Eyebrow>
        </Reveal>
        <Reveal>
          <div className="mb-[22px] flex justify-center gap-[18px] font-mono text-[11.5px] text-muted">
            <span>
              <i className="mr-[6px] inline-block h-[9px] w-[9px] rounded-full align-middle bg-sky" />
              computational
            </span>
            <span>
              <i className="mr-[6px] inline-block h-[9px] w-[9px] rounded-full align-middle bg-mint" />
              biology
            </span>
          </div>
        </Reveal>
        <Reveal>
          <div className="mx-auto flex max-w-[860px] flex-wrap justify-center gap-3">
            {skills.map((s) => (
              <div
                key={s.name}
                title={s.description}
                className="flex items-center gap-[10px] rounded-[11px] border border-border bg-surface px-[15px] py-[11px] text-[14px] transition hover:-translate-y-0.5 hover:border-primary hover:shadow-[var(--shadow)]"
              >
                <span
                  className={`h-[9px] w-[9px] flex-none rounded-full ${
                    BIO.test(s.name) ? "bg-mint" : "bg-sky"
                  }`}
                />
                {s.name}
              </div>
            ))}
          </div>
        </Reveal>
      </div>
    </section>
  );
}
