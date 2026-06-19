import type { BlogDetail, BlogListItem } from "@/lib/types";
import InnerHeader from "@/components/InnerHeader";
import StreamField from "@/components/streamfield/StreamField";
import Media from "@/components/Media";
import PostNav, { type NavLink } from "@/components/PostNav";

function fmtDate(d: string) {
  if (!d) return "";
  return new Date(d).toLocaleDateString("en-GB", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}

/** Presentational blog post, shared by the live page and the CMS preview. */
export default function BlogPostView({
  post,
  prev,
  next,
  related,
}: {
  post: BlogDetail;
  prev?: NavLink | null;
  next?: NavLink | null;
  related?: BlogListItem[];
}) {
  return (
    <>
      <InnerHeader />
      <main className="mx-auto max-w-5xl px-7 py-16">
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
            <Media
              src={post.hero_image.url}
              lqip={post.hero_lqip?.url}
              alt={post.hero_image.alt}
              width={post.hero_image.width}
              height={post.hero_image.height}
              className="w-full rounded-2xl border border-border"
              imgClassName="w-full h-auto"
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
      <PostNav base="/blog" prev={prev} next={next} related={related} />
    </>
  );
}
