import type { HomeSection } from "@/lib/types";
import { mediaUrl } from "@/lib/api";
import Eyebrow from "../Eyebrow";
import Reveal from "../Reveal";

export default function Gallery({ section }: { section: HomeSection }) {
  const items = (section.value.items || []).filter((it) => it.image);
  if (!items.length) return null;
  const title = section.value.title || "Gallery";

  return (
    <section id={`gallery-${section.id}`} className="border-b border-border py-24">
      <div className="mx-auto max-w-5xl px-7">
        <Reveal>
          <Eyebrow centered>{title}</Eyebrow>
        </Reveal>
        {section.value.intro && (
          <Reveal>
            <p className="mx-auto mb-8 max-w-2xl text-center text-muted">
              {section.value.intro}
            </p>
          </Reveal>
        )}
        <Reveal>
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
            {items.map((it, i) => (
              <figure key={i} className="group overflow-hidden rounded-xl border border-border">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={mediaUrl(it.image!.thumb || it.image!.url)}
                  alt={it.image!.alt}
                  className="aspect-square w-full object-cover transition duration-500 group-hover:scale-105"
                />
                {it.caption && (
                  <figcaption className="px-3 py-2 font-mono text-[11.5px] text-muted">
                    {it.caption}
                  </figcaption>
                )}
              </figure>
            ))}
          </div>
        </Reveal>
      </div>
    </section>
  );
}
