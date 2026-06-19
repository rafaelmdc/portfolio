import type { StreamBlock, ImageRendition } from "@/lib/types";
import { mediaUrl } from "@/lib/api";
import CodeBlock from "./CodeBlock";

/* ---------- helpers ---------- */
function embedSrc(url: string): string | null {
  const yt = url.match(/(?:youtube\.com\/watch\?v=|youtu\.be\/)([\w-]+)/);
  if (yt) return `https://www.youtube.com/embed/${yt[1]}`;
  const vimeo = url.match(/vimeo\.com\/(\d+)/);
  if (vimeo) return `https://player.vimeo.com/video/${vimeo[1]}`;
  return null;
}

const RADIUS: Record<string, string> = {
  none: "rounded-none",
  sm: "rounded",
  md: "rounded-lg",
  lg: "rounded-2xl",
};

/* ---------- block components ---------- */
function ImageBlock({ value }: { value: Record<string, unknown> }) {
  const img = value.image as ImageRendition | null;
  if (!img) return null;
  const alignment = (value.alignment as string) || "center";
  const widthPct = (value.width_pct as number) || 100;
  const radius = RADIUS[(value.radius as string) || "lg"] ?? "rounded-2xl";
  const caption = value.caption as string;
  const full = alignment === "full" || alignment === "wide";

  const el = (
    /* eslint-disable-next-line @next/next/no-img-element */
    <img
      src={mediaUrl(img.url)}
      alt={img.alt}
      width={img.width}
      height={img.height}
      className={`mx-auto block h-auto w-full border border-border ${radius}`}
    />
  );

  return (
    <figure
      className="my-7"
      style={{ maxWidth: full ? "100%" : `${widthPct}%`, marginInline: "auto" }}
    >
      {value.link_url ? (
        <a
          href={value.link_url as string}
          target={value.open_in_new ? "_blank" : undefined}
          rel="noopener noreferrer"
        >
          {el}
        </a>
      ) : (
        el
      )}
      {caption && (
        <figcaption className="mt-2 text-center font-mono text-[12px] text-muted">
          {caption}
        </figcaption>
      )}
    </figure>
  );
}

const CALLOUT: Record<string, string> = {
  info: "border-sky bg-sky",
  tip: "border-mint bg-mint",
  warn: "border-peach bg-peach",
  note: "border-hl bg-hl",
};

function block(b: StreamBlock): React.ReactNode {
  const v = b.value as Record<string, unknown>;
  switch (b.type) {
    case "heading": {
      const Tag = ((v.level as string) || "h2") as "h2" | "h3" | "h4";
      const size =
        Tag === "h2" ? "text-[30px]" : Tag === "h3" ? "text-[24px]" : "text-[20px]";
      return (
        <Tag className={`mb-3 mt-8 font-display font-medium ${size}`}>
          {v.text as string}
        </Tag>
      );
    }
    case "paragraph":
      return (
        <div
          className="rich my-2"
          style={{ textAlign: (v.alignment as CanvasTextAlign) || "left" }}
          dangerouslySetInnerHTML={{ __html: v.text as string }}
        />
      );
    case "image":
      return <ImageBlock value={v} />;
    case "quote":
      return (
        <blockquote className="my-7 border-l-[3px] border-peach pl-5 font-display text-[22px] italic leading-[1.4]">
          {typeof b.value === "string" ? b.value : (v.quote as string)}
        </blockquote>
      );
    case "embed": {
      const url = (v.url as string) || (b.value as string);
      const src = embedSrc(url);
      return (
        <figure className="my-7">
          {src ? (
            <div className="relative aspect-video overflow-hidden rounded-xl border border-border">
              <iframe
                src={src}
                className="absolute inset-0 h-full w-full"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
              />
            </div>
          ) : (
            <a href={url} className="text-primary underline" target="_blank" rel="noopener noreferrer">
              {url}
            </a>
          )}
          {v.caption ? (
            <figcaption className="mt-2 text-center font-mono text-[12px] text-muted">
              {v.caption as string}
            </figcaption>
          ) : null}
        </figure>
      );
    }
    case "callout":
      return (
        <div className={`my-6 rounded-xl border-l-4 p-4 ${CALLOUT[(v.style as string) || "info"]}`}>
          {v.title ? <p className="mb-1 font-display text-[17px] font-medium">{v.title as string}</p> : null}
          <div className="rich" dangerouslySetInnerHTML={{ __html: v.text as string }} />
        </div>
      );
    case "code":
      return <CodeBlock value={v} />;
    case "button":
      return (
        <p className="my-5">
          <a
            href={v.url as string}
            className="inline-flex items-center gap-2 rounded-[11px] border border-primary bg-primary px-[18px] py-3 font-mono text-[13px] text-[var(--on-primary)]"
          >
            {v.text as string}
          </a>
        </p>
      );
    case "divider":
      return <hr className="my-9 border-border" />;
    case "spacer": {
      const h = b.value === "lg" ? "h-16" : b.value === "sm" ? "h-4" : "h-9";
      return <div className={h} />;
    }
    case "gallery": {
      const images = (v.images as ImageRendition[]) || [];
      return (
        <div className="my-7 grid grid-cols-2 gap-3 sm:grid-cols-3">
          {images.map((im, i) => (
            /* eslint-disable-next-line @next/next/no-img-element */
            <img
              key={i}
              src={mediaUrl(im.thumb || im.url)}
              alt={im.alt}
              className="aspect-square w-full rounded-lg border border-border object-cover"
            />
          ))}
        </div>
      );
    }
    case "section": {
      const inner = (v.inner as StreamBlock[]) || [];
      const bg =
        v.background === "soft"
          ? "bg-surface"
          : v.background === "contrast"
            ? "bg-hl"
            : "";
      return (
        <div className={`my-6 rounded-2xl ${bg} ${bg ? "p-6" : ""}`}>
          <StreamField blocks={inner} />
        </div>
      );
    }
    case "pdfs": {
      type Pdf = { label?: string; note?: string; url?: string; open_in_new?: boolean };
      const docs = (v.documents as Pdf[]) || [];
      return (
        <div className="my-6 rounded-xl border border-border bg-surface p-5">
          {v.title ? <p className="font-display text-[18px] font-medium">{v.title as string}</p> : null}
          {v.description ? <p className="mb-3 text-[14px] text-muted">{v.description as string}</p> : null}
          <div className="flex flex-wrap gap-x-4 gap-y-3">
            {docs.map((d, i) =>
              d.url ? (
                <span key={i} className="flex flex-col gap-1">
                  <span className="flex items-center gap-1.5">
                    <span className="font-mono text-[12px] text-ink">{d.label || "PDF"}</span>
                    <a
                      href={mediaUrl(d.url)}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1 rounded-md bg-mint px-2.5 py-1.5 font-mono text-[11.5px] text-chip-ink transition hover:-translate-y-0.5"
                    >
                      ⤢ view
                    </a>
                    <a
                      href={mediaUrl(d.url)}
                      download
                      className="inline-flex items-center gap-1 rounded-md border border-border px-2.5 py-1.5 font-mono text-[11.5px] text-muted transition hover:-translate-y-0.5 hover:text-ink"
                    >
                      ↓ download
                    </a>
                  </span>
                  {d.note ? <span className="text-[11px] text-muted">{d.note}</span> : null}
                </span>
              ) : null,
            )}
          </div>
        </div>
      );
    }
    default:
      return null;
  }
}

export default function StreamField({ blocks }: { blocks: StreamBlock[] }) {
  if (!blocks?.length) return null;
  return (
    <>
      {blocks.map((b) => (
        <div key={b.id}>{block(b)}</div>
      ))}
    </>
  );
}
