import Link from "next/link";
import InnerHeader from "@/components/InnerHeader";

export default function NotFound() {
  return (
    <>
      <InnerHeader />
      <main className="mx-auto flex min-h-[70vh] max-w-3xl flex-col items-center justify-center gap-4 px-7 text-center">
        <p className="font-mono text-[13px] tracking-[0.06em] text-primary">404 — not found</p>
        <h1 className="font-display text-[clamp(32px,6vw,56px)] font-medium">
          This page didn&apos;t sequence.
        </h1>
        <p className="max-w-md text-[15px] text-muted">
          The link may be broken or the page may have moved. Try the home page, or hit{" "}
          <kbd className="rounded border border-border bg-surface px-1.5 py-0.5 font-mono text-[12px]">
            ⌘K
          </kbd>{" "}
          to search.
        </p>
        <div className="mt-2 flex flex-wrap justify-center gap-3">
          <Link
            href="/"
            className="inline-flex items-center gap-2 rounded-[11px] border border-primary bg-primary px-[18px] py-2.5 font-mono text-[13px] text-[var(--on-primary)] transition hover:-translate-y-0.5"
          >
            ← Home
          </Link>
          <Link
            href="/blog"
            className="inline-flex items-center gap-2 rounded-[11px] border border-border bg-surface px-[18px] py-2.5 font-mono text-[13px] transition hover:-translate-y-0.5"
          >
            Read the blog
          </Link>
        </div>
      </main>
    </>
  );
}
