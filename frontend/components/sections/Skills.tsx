"use client";

import { useState } from "react";
import type { SiteBundle } from "@/lib/types";
import Eyebrow from "../Eyebrow";
import Reveal from "../Reveal";

const BIO = /biolog|genetic|ecolog|evolu|physiolog|microbio|organism|taxonom|molecular|anatom/i;

type Cat = "bio" | "comp";

export default function Skills({
  bundle,
  num,
  title,
}: {
  bundle: SiteBundle;
  num: number;
  title?: string;
}) {
  const skills = bundle.skills;
  // Clicking a tag (or a legend entry) highlights that category, dims the rest.
  const [active, setActive] = useState<Cat | null>(null);
  if (!skills.length) return null;

  const toggle = (c: Cat) => setActive((prev) => (prev === c ? null : c));

  return (
    <section id="skills" className="border-b border-border py-24">
      <div className="mx-auto max-w-5xl px-7">
        <Reveal>
          <Eyebrow centered>§{num} — {title || bundle.copy.skills_title || "Skills"}</Eyebrow>
        </Reveal>
        <Reveal>
          <div className="mb-[22px] flex justify-center gap-[18px] font-mono text-[11.5px]">
            <button
              type="button"
              onClick={() => toggle("comp")}
              aria-pressed={active === "comp"}
              className={`transition ${active === "comp" ? "text-ink" : "text-muted hover:text-ink"}`}
            >
              <i className="mr-[6px] inline-block h-[9px] w-[9px] rounded-full align-middle bg-comp" />
              computational
            </button>
            <button
              type="button"
              onClick={() => toggle("bio")}
              aria-pressed={active === "bio"}
              className={`transition ${active === "bio" ? "text-ink" : "text-muted hover:text-ink"}`}
            >
              <i className="mr-[6px] inline-block h-[9px] w-[9px] rounded-full align-middle bg-bio" />
              biology
            </button>
          </div>
        </Reveal>
        <Reveal>
          <div className="mx-auto flex max-w-[860px] flex-wrap justify-center gap-3">
            {skills.map((s) => {
              const cat: Cat = BIO.test(s.name) ? "bio" : "comp";
              const dim = active !== null && active !== cat;
              const hot = active === cat;
              return (
                <button
                  key={s.name}
                  type="button"
                  onClick={() => toggle(cat)}
                  className={`group relative flex items-center gap-[10px] rounded-[11px] border bg-surface px-[15px] py-[11px] text-[14px] transition duration-150 hover:-translate-y-0.5 hover:shadow-[var(--shadow)] ${
                    hot ? "border-primary shadow-[var(--shadow)]" : "border-border hover:border-primary"
                  } ${dim ? "opacity-40" : "opacity-100"}`}
                >
                  <span
                    className={`h-[9px] w-[9px] flex-none rounded-full ${
                      cat === "bio" ? "bg-bio" : "bg-comp"
                    }`}
                  />
                  {s.name}
                  {s.description && (
                    <span
                      role="tooltip"
                      className="pointer-events-none invisible absolute bottom-[calc(100%+8px)] left-1/2 z-50 w-max max-w-[240px] -translate-x-1/2 translate-y-1 rounded-lg border border-border bg-surface px-3 py-2 text-left text-[12.5px] font-normal leading-snug text-ink shadow-[var(--shadow)] transition duration-100 group-hover:visible group-hover:translate-y-0"
                    >
                      {s.description}
                    </span>
                  )}
                </button>
              );
            })}
          </div>
        </Reveal>
      </div>
    </section>
  );
}
