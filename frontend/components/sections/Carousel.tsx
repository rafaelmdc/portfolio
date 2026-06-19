"use client";

import { useCallback, useEffect, useState } from "react";
import type { HomeSection } from "@/lib/types";
import { mediaUrl } from "@/lib/api";
import Eyebrow from "../Eyebrow";

export default function Carousel({ section }: { section: HomeSection }) {
  const slides = (section.value.slides || []).filter((s) => s.image);
  const [i, setI] = useState(0);
  const n = slides.length;
  const autoplay = section.value.autoplay !== false;

  const go = useCallback((d: number) => setI((p) => (p + d + n) % n), [n]);

  useEffect(() => {
    if (!autoplay || n < 2) return;
    const t = setInterval(() => setI((p) => (p + 1) % n), 5000);
    return () => clearInterval(t);
  }, [autoplay, n]);

  if (!n) return null;
  const title = section.value.title;

  return (
    <section id={`carousel-${section.id}`} className="border-b border-border py-24">
      <div className="mx-auto max-w-5xl px-7">
        {title && (
          <Eyebrow centered>{title}</Eyebrow>
        )}
        {section.value.intro && (
          <p className="mx-auto mb-8 max-w-2xl text-center text-muted">
            {section.value.intro}
          </p>
        )}
        <div className="relative overflow-hidden rounded-2xl border border-border bg-surface shadow-[var(--shadow)]">
          <div
            className="flex transition-transform duration-500 ease-out"
            style={{ transform: `translateX(-${i * 100}%)` }}
          >
            {slides.map((s, idx) => {
              const media = (
                /* eslint-disable-next-line @next/next/no-img-element */
                <img
                  src={mediaUrl(s.image!.url)}
                  alt={s.image!.alt}
                  className="h-full w-full object-cover"
                />
              );
              return (
                <div key={idx} className="relative aspect-[16/9] w-full flex-none">
                  {s.link ? (
                    <a href={s.link} target="_blank" rel="noopener noreferrer">
                      {media}
                    </a>
                  ) : (
                    media
                  )}
                  {s.caption && (
                    <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/60 to-transparent px-5 py-4 font-mono text-[13px] text-white">
                      {s.caption}
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          {n > 1 && (
            <>
              <button
                onClick={() => go(-1)}
                aria-label="Previous slide"
                className="absolute left-3 top-1/2 grid h-9 w-9 -translate-y-1/2 place-items-center rounded-full border border-border bg-bg/80 backdrop-blur transition hover:border-primary"
              >
                ‹
              </button>
              <button
                onClick={() => go(1)}
                aria-label="Next slide"
                className="absolute right-3 top-1/2 grid h-9 w-9 -translate-y-1/2 place-items-center rounded-full border border-border bg-bg/80 backdrop-blur transition hover:border-primary"
              >
                ›
              </button>
              <div className="absolute inset-x-0 bottom-3 flex justify-center gap-2">
                {slides.map((_, idx) => (
                  <button
                    key={idx}
                    onClick={() => setI(idx)}
                    aria-label={`Go to slide ${idx + 1}`}
                    className={`h-2 rounded-full transition-all ${
                      idx === i ? "w-5 bg-primary" : "w-2 bg-border"
                    }`}
                  />
                ))}
              </div>
            </>
          )}
        </div>
      </div>
    </section>
  );
}
