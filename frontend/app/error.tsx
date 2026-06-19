"use client";

import Link from "next/link";

export default function Error({ reset }: { error: Error & { digest?: string }; reset: () => void }) {
  return (
    <main className="mx-auto flex min-h-screen max-w-3xl flex-col items-center justify-center gap-4 px-7 text-center">
      <p className="font-mono text-[13px] tracking-[0.06em] text-primary">500 — something broke</p>
      <h1 className="font-display text-[clamp(32px,6vw,56px)] font-medium">
        A pipeline step failed.
      </h1>
      <p className="max-w-md text-[15px] text-muted">
        An unexpected error occurred. You can try again, or head back home.
      </p>
      <div className="mt-2 flex flex-wrap justify-center gap-3">
        <button
          onClick={reset}
          className="inline-flex items-center gap-2 rounded-[11px] border border-primary bg-primary px-[18px] py-2.5 font-mono text-[13px] text-[var(--on-primary)] transition hover:-translate-y-0.5"
        >
          ↻ Try again
        </button>
        <Link
          href="/"
          className="inline-flex items-center gap-2 rounded-[11px] border border-border bg-surface px-[18px] py-2.5 font-mono text-[13px] transition hover:-translate-y-0.5"
        >
          ← Home
        </Link>
      </div>
    </main>
  );
}
