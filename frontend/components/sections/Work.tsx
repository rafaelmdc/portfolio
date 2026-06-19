import Link from "next/link";
import type { ProjectListItem } from "@/lib/types";
import { mediaUrl } from "@/lib/api";
import Eyebrow from "../Eyebrow";
import Reveal from "../Reveal";

export default function Work({
  projects,
  num,
  title,
}: {
  projects: ProjectListItem[];
  num: number;
  title?: string;
}) {
  if (!projects.length) return null;

  return (
    <section id="work" className="border-b border-border py-24">
      <div className="mx-auto max-w-5xl px-7">
        <Reveal>
          <Eyebrow>§{num} — {title || "Selected work"}</Eyebrow>
        </Reveal>
        {projects.map((p) => {
          const slug = p.meta.slug;
          return (
            <Reveal key={p.id}>
              <Link
                href={`/portfolio/${slug}`}
                className="mb-4 grid grid-cols-1 items-center gap-6 rounded-2xl border border-border bg-surface p-[22px] shadow-[var(--shadow)] transition hover:-translate-y-[3px] md:grid-cols-[120px_1fr_auto]"
              >
                <div
                  className="h-24 rounded-xl bg-cover bg-center"
                  style={{
                    backgroundImage: p.cover_thumb
                      ? `url(${mediaUrl(p.cover_thumb.thumb)})`
                      : "linear-gradient(135deg, var(--sky), var(--mint))",
                  }}
                />
                <div>
                  <h3 className="mb-1.5 font-display text-[23px] font-medium">
                    {p.title}
                  </h3>
                  {p.subtitle && (
                    <p className="m-0 text-[14.5px] text-muted">{p.subtitle}</p>
                  )}
                  {p.tag_names.length > 0 && (
                    <div className="mt-[11px] flex flex-wrap gap-[7px]">
                      {p.tag_names.map((t) => (
                        <span
                          key={t}
                          className="rounded-md bg-mint px-2 py-[3px] font-mono text-[11px] text-chip-ink"
                        >
                          {t}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
                <span className="hidden font-mono text-[20px] text-primary md:block">
                  →
                </span>
              </Link>
            </Reveal>
          );
        })}
      </div>
    </section>
  );
}
