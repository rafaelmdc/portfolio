import type { ProjectDetail, ProjectListItem } from "@/lib/types";
import InnerHeader from "@/components/InnerHeader";
import StreamField from "@/components/streamfield/StreamField";
import Media from "@/components/Media";
import PostNav, { type NavLink } from "@/components/PostNav";

function Section({ heading, html }: { heading: string; html: string }) {
  if (!html) return null;
  return (
    <div className="mb-8">
      <h2 className="mb-2 font-mono text-[12px] uppercase tracking-[0.08em] text-primary-ink">
        {heading}
      </h2>
      <div
        className="text-[16.5px] leading-[1.7] [&_a]:text-primary-ink [&_a]:underline"
        dangerouslySetInnerHTML={{ __html: html }}
      />
    </div>
  );
}

/** Presentational portfolio project, shared by the live page and CMS preview. */
export default function ProjectView({
  project,
  prev,
  next,
  related,
}: {
  project: ProjectDetail;
  prev?: NavLink | null;
  next?: NavLink | null;
  related?: ProjectListItem[];
}) {
  const hasCaseStudy =
    project.problem || project.approach || project.outcome || project.result_metric;

  return (
    <>
      <InnerHeader />
      <main className="mx-auto max-w-5xl px-7 py-16">
        <div className="mb-3 font-mono text-[12px] text-muted">§ project</div>
        <h1 className="mb-3 font-display text-[clamp(32px,5.5vw,52px)] font-medium leading-[1.08]">
          {project.title}
        </h1>
        {project.subtitle && <p className="mb-5 text-[18px] text-muted">{project.subtitle}</p>}

        {project.result_metric && (
          <div className="mb-6 inline-flex items-center gap-2 rounded-xl border border-border bg-hl px-4 py-2 font-mono text-[14px] text-chip-ink">
            <span aria-hidden>↳</span>
            {project.result_metric}
          </div>
        )}

        <div className="mb-7 flex flex-wrap gap-[10px]">
          {project.external_url && (
            <a
              href={project.external_url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 rounded-[11px] border border-primary bg-primary px-[18px] py-2.5 font-mono text-[13px] text-[var(--on-primary)] transition hover:-translate-y-0.5"
            >
              ↗ Live
            </a>
          )}
          {project.github_url && (
            <a
              href={project.github_url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 rounded-[11px] border border-border bg-surface px-[18px] py-2.5 font-mono text-[13px] transition hover:-translate-y-0.5"
            >
              ↗ Source
            </a>
          )}
        </div>

        {project.tech_list.length > 0 && (
          <div className="mb-7 flex flex-wrap gap-[7px]">
            {project.tech_list.map((t) => (
              <span
                key={t}
                className="rounded-md border border-border bg-surface px-2 py-[3px] font-mono text-[11px] text-chip-ink"
              >
                {t}
              </span>
            ))}
          </div>
        )}

        {project.cover_image && (
          <Media
            src={project.cover_image.url}
            lqip={project.cover_lqip?.url}
            alt={project.cover_image.alt}
            width={project.cover_image.width}
            height={project.cover_image.height}
            className="mb-10 w-full rounded-2xl border border-border"
            imgClassName="w-full h-auto"
          />
        )}

        {hasCaseStudy && (
          <div className="mb-10 rounded-2xl border border-border bg-surface p-6">
            <Section heading="The problem" html={project.problem} />
            <Section heading="Approach" html={project.approach} />
            <Section heading="Outcome" html={project.outcome} />
          </div>
        )}

        {project.body.length > 0 && (
          <article className="text-[16.5px] leading-[1.75]">
            <StreamField blocks={project.body} />
          </article>
        )}
      </main>
      <PostNav base="/portfolio" prev={prev} next={next} related={related} />
    </>
  );
}
