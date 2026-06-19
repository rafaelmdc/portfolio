"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import ThemeToggle from "./ThemeToggle";

export type NavLink = { href: string; n: string; label: string };

export default function Nav({ links }: { links: NavLink[] }) {
  const [open, setOpen] = useState(false);

  // Shift + 1..9 jumps to the matching §-numbered section. Uses the physical
  // key code (so the Shift "!" remapping doesn't matter) and ignores typing.
  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if (!e.shiftKey || e.ctrlKey || e.metaKey || e.altKey) return;
      const m = /^Digit([1-9])$/.exec(e.code);
      if (!m) return;
      const el = document.activeElement as HTMLElement | null;
      if (el && (el.tagName === "INPUT" || el.tagName === "TEXTAREA" || el.isContentEditable))
        return;
      const link = links.find((l) => l.n === `§${m[1]}`);
      if (!link) return;
      const target = document.getElementById(link.href.slice(1));
      if (!target) return;
      e.preventDefault();
      target.scrollIntoView({ behavior: "smooth" });
      history.replaceState(null, "", link.href);
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [links]);

  return (
    <header className="sticky top-0 z-50 border-b border-border bg-bg/80 backdrop-blur-md backdrop-saturate-150">
      <nav className="mx-auto flex h-[62px] max-w-5xl items-center gap-7 px-7">
        <span className="font-mono text-[13px] font-medium">
          rafael<span className="text-primary">.duarte-correia</span>()
        </span>

        {/* desktop links */}
        <div className="ml-auto hidden gap-[22px] md:flex">
          {links.map((l, i) => (
            <a
              key={l.href}
              href={l.href}
              title={`Shift+${i + 1}`}
              className="font-mono text-[12.5px] text-muted transition hover:text-ink"
            >
              <span className="text-primary/70">{l.n}</span> {l.label}
            </a>
          ))}
          <Link
            href="/blog"
            className="font-mono text-[12.5px] text-muted transition hover:text-ink"
          >
            <span className="text-primary/70">↗</span> blog
          </Link>
        </div>

        <div className="ml-auto flex items-center gap-2.5 md:ml-0">
          <span className="hidden rounded-md border border-border bg-surface px-2 py-1 font-mono text-[11px] text-muted sm:inline">
            ⌘K
          </span>
          <ThemeToggle />
          <button
            onClick={() => setOpen((o) => !o)}
            aria-label="Menu"
            aria-expanded={open}
            className="grid h-[34px] w-[34px] place-items-center rounded-[9px] border border-border bg-surface text-[15px] transition hover:border-primary md:hidden"
          >
            {open ? "✕" : "☰"}
          </button>
        </div>
      </nav>

      {/* mobile dropdown */}
      {open && (
        <div className="border-t border-border bg-bg px-7 py-3 md:hidden">
          {links.map((l) => (
            <a
              key={l.href}
              href={l.href}
              onClick={() => setOpen(false)}
              className="block py-2 font-mono text-[14px] text-muted transition hover:text-ink"
            >
              <span className="text-primary/70">{l.n}</span> {l.label}
            </a>
          ))}
          <Link
            href="/blog"
            onClick={() => setOpen(false)}
            className="block py-2 font-mono text-[14px] text-muted transition hover:text-ink"
          >
            <span className="text-primary/70">↗</span> blog
          </Link>
        </div>
      )}
    </header>
  );
}
