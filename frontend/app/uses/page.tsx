import type { Metadata } from "next";
import { getSiteBundle } from "@/lib/api";
import InnerHeader from "@/components/InnerHeader";
import Eyebrow from "@/components/Eyebrow";
import Reveal from "@/components/Reveal";

export const metadata: Metadata = {
  title: "Uses — Rafael Correia",
  description: "The tools, software, and gear I use day to day.",
};

export const dynamic = "force-dynamic";

export default async function UsesPage() {
  const bundle = await getSiteBundle();
  const { intro, categories } = bundle.uses;

  return (
    <>
      <InnerHeader />
      <main className="mx-auto max-w-3xl px-7 py-20">
        <Reveal>
          <Eyebrow>§ — Uses</Eyebrow>
          <h1 className="mb-4 font-display text-[clamp(34px,6vw,56px)] font-medium">
            What I use
          </h1>
          {intro && <p className="mb-12 max-w-2xl text-[17px] text-muted">{intro}</p>}
        </Reveal>

        {categories.length === 0 && (
          <p className="font-mono text-[14px] text-muted">Coming soon.</p>
        )}

        <div className="flex flex-col gap-10">
          {categories.map((cat) => (
            <Reveal key={cat.heading}>
              <section>
                <h2 className="mb-4 font-mono text-[12px] uppercase tracking-[0.08em] text-primary-ink">
                  {cat.heading}
                </h2>
                <ul className="flex flex-col">
                  {cat.items.map((it, i) => (
                    <li
                      key={`${it.name}-${i}`}
                      className={`flex flex-col gap-1 py-3 sm:flex-row sm:items-baseline sm:justify-between sm:gap-6 ${
                        i > 0 ? "border-t border-dashed border-border" : ""
                      }`}
                    >
                      <span className="font-display text-[16.5px] font-medium">
                        {it.url ? (
                          <a
                            href={it.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="underline decoration-border underline-offset-4 hover:decoration-primary"
                          >
                            {it.name}
                          </a>
                        ) : (
                          it.name
                        )}
                      </span>
                      {it.detail && (
                        <span className="text-[14.5px] text-muted sm:text-right">{it.detail}</span>
                      )}
                    </li>
                  ))}
                </ul>
              </section>
            </Reveal>
          ))}
        </div>
      </main>
    </>
  );
}
