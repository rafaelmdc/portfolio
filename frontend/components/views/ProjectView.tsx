import type { ProjectDetail } from "@/lib/types";
import { mediaUrl } from "@/lib/api";
import InnerHeader from "@/components/InnerHeader";
import StreamField from "@/components/streamfield/StreamField";

/** Presentational portfolio project, shared by the live page and CMS preview. */
export default function ProjectView({ project }: { project: ProjectDetail }) {
  return (
    <>
      <InnerHeader />
      <main className="mx-auto max-w-5xl px-7 py-16">
        <div className="mb-3 font-mono text-[12px] text-muted">§ project</div>
        <h1 className="mb-3 font-display text-[clamp(32px,5.5vw,52px)] font-medium leading-[1.08]">
          {project.title}
        </h1>
        {project.subtitle && (
          <p className="mb-5 text-[18px] text-muted">{project.subtitle}</p>
        )}

        <div className="mb-8 flex flex-wrap gap-[10px]">
          {project.external_url && (
            <a
              href={project.external_url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 rounded-[11px] border border-primary bg-primary px-[18px] py-2.5 font-mono text-[13px] text-[var(--on-primary)]"
            >
              ↗ Live
            </a>
          )}
          {project.github_url && (
            <a
              href={project.github_url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 rounded-[11px] border border-border bg-surface px-[18px] py-2.5 font-mono text-[13px]"
            >
              ↗ GitHub
            </a>
          )}
        </div>

        {project.tag_names.length > 0 && (
          <div className="mb-8 flex flex-wrap gap-[7px]">
            {project.tag_names.map((t) => (
              <span
                key={t}
                className="rounded-md bg-mint px-2 py-[3px] font-mono text-[11px] text-chip-ink"
              >
                {t}
              </span>
            ))}
          </div>
        )}

        {project.cover_image && (
          /* eslint-disable-next-line @next/next/no-img-element */
          <img
            src={mediaUrl(project.cover_image.url)}
            alt={project.cover_image.alt}
            className="mb-10 w-full rounded-2xl border border-border"
          />
        )}

        <article className="text-[16.5px] leading-[1.75]">
          <StreamField blocks={project.body} />
        </article>
      </main>
    </>
  );
}
