import type { SiteBundle } from "@/lib/types";
import Eyebrow from "../Eyebrow";
import Reveal from "../Reveal";

type Fact = { label: string; value: string };

export default function About({
  bundle,
  num,
  title,
}: {
  bundle: SiteBundle;
  num: number;
  title?: string;
}) {
  const { copy, github, awards, publications, stats, about_extra } = bundle;

  // Each row is shown only when toggled on (CMS) and its data exists.
  const facts: Fact[] = [];
  if (stats.stat_status && about_extra.current_status)
    facts.push({ label: "currently", value: about_extra.current_status });
  if (stats.stat_domain && about_extra.primary_domain)
    facts.push({ label: "domain", value: about_extra.primary_domain });
  if (stats.stat_focus && copy.about_focus)
    facts.push({ label: "focus", value: copy.about_focus });
  if (stats.stat_building && about_extra.building_since)
    facts.push({ label: "building since", value: String(about_extra.building_since) });
  if (stats.stat_projects && about_extra.projects_count)
    facts.push({ label: "projects shipped", value: String(about_extra.projects_count) });
  if (stats.stat_repos && github?.public_repos != null)
    facts.push({ label: "public repos", value: String(github.public_repos) });
  if (stats.stat_stars && github?.total_stars)
    facts.push({ label: "total stars", value: String(github.total_stars) });
  if (stats.stat_language && github?.top_language)
    facts.push({ label: "top language", value: github.top_language });
  if (stats.stat_followers && github?.followers != null)
    facts.push({ label: "followers", value: String(github.followers) });
  if (stats.stat_commits && github?.total_commits != null)
    facts.push({ label: "commits", value: github.total_commits.toLocaleString() });
  if (stats.stat_publications && publications.flat.length)
    facts.push({ label: "publications", value: String(publications.flat.length) });
  if (stats.stat_honors && awards.length)
    facts.push({ label: "honors", value: awards[0].title });

  return (
    <section id="about" className="border-b border-border py-24">
      <div className="mx-auto max-w-5xl px-7">
        <Reveal>
          <Eyebrow>§{num} — {title || copy.about_title || "About"}</Eyebrow>
        </Reveal>
        <div className="grid grid-cols-1 items-center gap-[54px] md:grid-cols-[1.4fr_0.9fr]">
          <Reveal>
            <h2 className="mb-5 font-display text-[clamp(28px,4vw,40px)] font-medium">
              {copy.about_intro_headline || "Pipelines that connect biology with clean code."}
            </h2>
            <p className="mb-[18px]">
              {copy.about_lead ||
                "I'm a bioinformatics student interested in using data and code to study biological systems."}
            </p>
            {copy.about_intro_body && <p className="mb-[18px]">{copy.about_intro_body}</p>}
            {copy.about_quote && (
              <blockquote className="mt-[22px] border-l-[3px] border-peach pl-5 font-display text-[21px] italic leading-[1.4]">
                “{copy.about_quote}”
              </blockquote>
            )}
          </Reveal>

          <Reveal>
            <div className="rounded-2xl border border-border bg-surface p-5 shadow-[var(--shadow)]">
              <h3 className="mb-[14px] font-mono text-[13px] font-normal tracking-[0.04em] text-muted">
                {"// at a glance"}
              </h3>
              {facts.map((f, i) => (
                <div
                  key={f.label}
                  className={`flex justify-between gap-3 py-[9px] font-mono text-[13px] ${
                    i > 0 ? "border-t border-dashed border-border" : ""
                  }`}
                >
                  <span className="whitespace-nowrap text-muted">{f.label}</span>
                  <span className="text-right font-medium">{f.value}</span>
                </div>
              ))}
            </div>
          </Reveal>
        </div>
      </div>
    </section>
  );
}
