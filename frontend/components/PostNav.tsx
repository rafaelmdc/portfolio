import Link from "next/link";
import type { BlogListItem, ProjectListItem } from "@/lib/types";
import Media from "./Media";

export type NavLink = { title: string; slug: string };
type RelItem = BlogListItem | ProjectListItem;

/** A small related-content card (reuses the list-card look). */
function RelCard({ item, base }: { item: RelItem; base: string }) {
  const thumb = item.card_thumb;
  return (
    <Link
      href={`${base}/${item.meta.slug}`}
      className="group flex flex-col gap-3 rounded-2xl border border-border bg-surface p-3 transition hover:-translate-y-0.5 hover:shadow-[var(--shadow)]"
    >
      {thumb ? (
        <Media
          src={thumb.url}
          lqip={item.card_lqip?.url}
          alt={thumb.alt}
          className="h-28 w-full rounded-xl"
          imgClassName="h-full w-full object-cover"
        />
      ) : (
        <div
          className="h-28 w-full rounded-xl"
          style={{ background: "linear-gradient(135deg, var(--sky), var(--mint))" }}
        />
      )}
      <span className="font-display text-[15px] font-medium leading-snug">{item.title}</span>
    </Link>
  );
}

/**
 * Prev/next pager + an optional "related" strip, shared by blog and project
 * detail pages. `base` is "/blog" or "/portfolio".
 */
export default function PostNav({
  base,
  prev,
  next,
  related,
}: {
  base: string;
  prev?: NavLink | null;
  next?: NavLink | null;
  related?: RelItem[];
}) {
  const hasPager = prev || next;
  const hasRelated = related && related.length > 0;
  if (!hasPager && !hasRelated) return null;

  return (
    <nav className="mx-auto mt-16 max-w-5xl border-t border-border px-7 pt-10">
      {hasPager && (
        <div className="mb-12 flex flex-col gap-4 sm:flex-row sm:justify-between">
          {prev ? (
            <Link
              href={`${base}/${prev.slug}`}
              className="group max-w-[48%] flex flex-col gap-1 text-left"
            >
              <span className="font-mono text-[11px] text-muted">← Older</span>
              <span className="font-display text-[16px] font-medium group-hover:text-primary-ink">
                {prev.title}
              </span>
            </Link>
          ) : (
            <span />
          )}
          {next ? (
            <Link
              href={`${base}/${next.slug}`}
              className="group ml-auto max-w-[48%] flex flex-col gap-1 text-right"
            >
              <span className="font-mono text-[11px] text-muted">Newer →</span>
              <span className="font-display text-[16px] font-medium group-hover:text-primary-ink">
                {next.title}
              </span>
            </Link>
          ) : (
            <span />
          )}
        </div>
      )}

      {hasRelated && (
        <div>
          <p className="mb-4 font-mono text-[12px] tracking-[0.05em] text-muted">{"// related"}</p>
          <div className="grid grid-cols-2 gap-4 md:grid-cols-3">
            {related!.map((item) => (
              <RelCard key={item.meta.slug} item={item} base={base} />
            ))}
          </div>
        </div>
      )}
    </nav>
  );
}
