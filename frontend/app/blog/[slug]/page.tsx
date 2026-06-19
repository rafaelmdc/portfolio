import { notFound } from "next/navigation";
import type { Metadata } from "next";
import { getBlogPost, getBlogPosts, mediaUrl } from "@/lib/api";
import InnerHeader from "@/components/InnerHeader";
import StreamField from "@/components/streamfield/StreamField";

export async function generateStaticParams() {
  const posts = await getBlogPosts();
  return posts.map((p) => ({ slug: p.meta.slug }));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>;
}): Promise<Metadata> {
  const { slug } = await params;
  const post = await getBlogPost(slug);
  if (!post) return {};
  return {
    title: `${post.title} — Rafael Correia`,
    description: post.intro || undefined,
  };
}

function fmtDate(d: string) {
  return new Date(d).toLocaleDateString("en-GB", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}

export default async function BlogPost({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const post = await getBlogPost(slug);
  if (!post) notFound();

  return (
    <>
      <InnerHeader />
      <main className="mx-auto max-w-3xl px-7 py-16">
        <div className="mb-3 flex flex-wrap items-center gap-2 font-mono text-[12px] text-muted">
          <span>{fmtDate(post.date)}</span>
          {post.reading_time_minutes ? <span>· {post.reading_time_minutes} min read</span> : null}
        </div>
        <h1 className="mb-4 font-display text-[clamp(32px,5.5vw,52px)] font-medium leading-[1.08]">
          {post.title}
        </h1>
        {post.intro && (
          <p className="mb-6 text-[18px] text-muted">{post.intro}</p>
        )}
        {post.tag_names.length > 0 && (
          <div className="mb-8 flex flex-wrap gap-[7px]">
            {post.tag_names.map((t) => (
              <span
                key={t}
                className="rounded-md bg-mint px-2 py-[3px] font-mono text-[11px] text-chip-ink"
              >
                {t}
              </span>
            ))}
          </div>
        )}
        {post.hero_image && (
          <figure className="mb-10">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={mediaUrl(post.hero_image.url)}
              alt={post.hero_image.alt}
              className="w-full rounded-2xl border border-border"
            />
            {post.hero_caption && (
              <figcaption className="mt-2 text-center font-mono text-[12px] text-muted">
                {post.hero_caption}
              </figcaption>
            )}
          </figure>
        )}
        <article className="text-[16.5px] leading-[1.75]">
          <StreamField blocks={post.body} />
        </article>
      </main>
    </>
  );
}
