import Link from "next/link";
import type { SiteBundle } from "@/lib/types";
import Reveal from "../Reveal";

export default function Contact({
  bundle,
  num,
  title,
}: {
  bundle: SiteBundle;
  num: number;
  title?: string;
}) {
  const c = bundle.contact;
  const email = c.email || "rafaelmdcorreia@gmail.com";
  const gh = c.github_username || bundle.github?.username;
  return (
    <footer id="contact" className="px-7 pb-[90px] pt-[72px] text-center">
      <div className="mx-auto max-w-5xl">
        <Reveal>
          <div className="mb-[18px] flex items-center justify-center gap-[10px] font-mono text-[12px] tracking-[0.06em] text-primary">
            §{num} — {title || "Contact"}
          </div>
        </Reveal>
        <Reveal>
          <h2 className="mb-[18px] font-display text-[clamp(30px,5vw,52px)] font-medium">
            {bundle.copy.contact_headline || "Let's turn biology into something runnable."}
          </h2>
        </Reveal>
        <Reveal>
          <div className="flex flex-wrap justify-center gap-[14px]">
            {c.show_email && (
              <a
                href={`mailto:${email}`}
                className="inline-flex items-center gap-[9px] rounded-[11px] border border-primary bg-primary px-[18px] py-3 font-mono text-[13px] text-[var(--on-primary)] transition hover:-translate-y-0.5"
              >
                ✦ Email me
              </a>
            )}
            {c.show_github && gh && (
              <a
                href={`https://github.com/${gh}`}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-[9px] rounded-[11px] border border-border bg-surface px-[18px] py-3 font-mono text-[13px] transition hover:-translate-y-0.5"
              >
                ↗ GitHub
              </a>
            )}
            {c.show_linkedin && c.linkedin_url && (
              <a
                href={c.linkedin_url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-[9px] rounded-[11px] border border-border bg-surface px-[18px] py-3 font-mono text-[13px] transition hover:-translate-y-0.5"
              >
                ↗ LinkedIn
              </a>
            )}
            {c.show_blog && (
              <Link
                href="/blog"
                className="inline-flex items-center gap-[9px] rounded-[11px] border border-border bg-surface px-[18px] py-3 font-mono text-[13px] transition hover:-translate-y-0.5"
              >
                ↗ Read the blog
              </Link>
            )}
          </div>
        </Reveal>
        <p className="mt-[26px] font-mono text-[13px] text-muted">
          {email} · {bundle.copy.contact_note || "always happy to talk research, code, or collaboration"}
        </p>
      </div>
    </footer>
  );
}
