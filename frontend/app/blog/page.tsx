import Link from "next/link";
import type { Metadata } from "next";
import { getBlogPosts, mediaUrl } from "@/lib/api";
import InnerHeader from "@/components/InnerHeader";
import Eyebrow from "@/components/Eyebrow";
import Reveal from "@/components/Reveal";

export const metadata: Metadata = {
  title: "Blog — Rafael Correia",
  description: "Notes on bioinformatics, pipelines, and data-driven biology.",
};

export const dynamic = "force-dynamic";

function fmtDate(d: string) {
  return new Date(d).toLocaleDateString("en-GB", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

export default async function BlogIndex() {
  const posts = await getBlogPosts();

  return (
    <>
      <InnerHeader />
      <main className="mx-auto max-w-3xl px-7 py-20">
        <Reveal>
          <Eyebrow>§ — Blog</Eyebrow>
          <h1 className="mb-12 font-display text-[clamp(34px,6vw,56px)] font-medium">
            Writing
          </h1>
        </Reveal>

        {posts.length === 0 && (
          <p className="font-mono text-[14px] text-muted">No posts yet.</p>
        )}

        <div className="flex flex-col gap-2">
          {posts.map((p) => (
            <Reveal key={p.id}>
              <Link
                href={`/blog/${p.meta.slug}`}
                className="grid grid-cols-1 gap-5 rounded-2xl border border-border bg-surface p-5 transition hover:-translate-y-[3px] hover:shadow-[var(--shadow)] sm:grid-cols-[160px_1fr]"
              >
                <div
                  className="h-28 rounded-xl bg-cover bg-center sm:h-full"
                  style={{
                    backgroundImage: p.hero_thumb
                      ? `url(${mediaUrl(p.hero_thumb.thumb)})`
                      : "linear-gradient(135deg, var(--sky), var(--hl))",
                  }}
                />
                <div>
                  <div className="mb-2 flex flex-wrap items-center gap-2 font-mono text-[11.5px] text-muted">
                    <span>{fmtDate(p.date)}</span>
                    {p.reading_time_minutes ? (
                      <span>· {p.reading_time_minutes} min</span>
                    ) : null}
                  </div>
                  <h2 className="mb-1.5 font-display text-[23px] font-medium leading-tight">
                    {p.title}
                  </h2>
                  {p.intro && (
                    <p className="m-0 text-[14.5px] text-muted">{p.intro}</p>
                  )}
                  {p.tag_names.length > 0 && (
                    <div className="mt-3 flex flex-wrap gap-[7px]">
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
              </Link>
            </Reveal>
          ))}
        </div>
      </main>
    </>
  );
}
