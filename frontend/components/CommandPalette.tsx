"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

type Dest = { label: string; hint: string; href: string };
type NavLink = { href: string; n: string; label: string };

const cap = (s: string) => s.charAt(0).toUpperCase() + s.slice(1);

// The home page publishes its live section list (order, titles, toggles) into
// a hidden element; the palette reads it so it always mirrors the navbar.
function readDests(): Dest[] {
  const home: Dest = { label: "Home", hint: "top", href: "/" };
  const blog: Dest = { label: "Blog", hint: "↗", href: "/blog" };
  let links: NavLink[] = [];
  try {
    const raw = document.getElementById("__nav_sections")?.dataset.sections;
    if (raw) links = JSON.parse(raw) as NavLink[];
  } catch {
    /* not on the home page — fall back to just Home + Blog */
  }
  const sections = links.map((l) => ({
    label: cap(l.label),
    hint: l.n,
    href: `/${l.href}`, // "#about" -> "/#about"
  }));
  return [home, ...sections, blog];
}

export default function CommandPalette() {
  const [open, setOpen] = useState(false);
  const [q, setQ] = useState("");
  const [active, setActive] = useState(0);
  const [dests, setDests] = useState<Dest[]>([]);

  const results = useMemo(() => {
    const s = q.trim().toLowerCase();
    return s ? dests.filter((d) => d.label.toLowerCase().includes(s)) : dests;
  }, [q, dests]);

  const close = useCallback(() => {
    setOpen(false);
    setQ("");
    setActive(0);
  }, []);

  const reveal = useCallback(() => {
    setDests(readDests());
    setOpen(true);
  }, []);

  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        if (open) close();
        else reveal();
      } else if (e.key === "Escape") {
        close();
      }
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, close, reveal]);

  if (!open) return null;

  function go(href: string) {
    close();
    // In-page anchors while already on the home page: scroll directly so it
    // works even when the hash matches the current URL.
    const hash = href.startsWith("/#") ? href.slice(1) : null;
    if (hash && window.location.pathname === "/") {
      const el = document.getElementById(hash.slice(1));
      if (el) {
        el.scrollIntoView({ behavior: "smooth" });
        history.replaceState(null, "", hash);
        return;
      }
    }
    if (href === "/" && window.location.pathname === "/") {
      window.scrollTo({ top: 0, behavior: "smooth" });
      history.replaceState(null, "", "/");
      return;
    }
    window.location.href = href;
  }

  return (
    <div
      className="fixed inset-0 z-[100] flex items-start justify-center bg-black/40 pt-[18vh]"
      onClick={close}
    >
      <div
        className="w-full max-w-md overflow-hidden rounded-2xl border border-border bg-surface shadow-[var(--shadow)]"
        onClick={(e) => e.stopPropagation()}
      >
        <input
          autoFocus
          value={q}
          onChange={(e) => {
            setQ(e.target.value);
            setActive(0);
          }}
          onKeyDown={(e) => {
            if (e.key === "ArrowDown") {
              e.preventDefault();
              setActive((a) => Math.min(a + 1, results.length - 1));
            } else if (e.key === "ArrowUp") {
              e.preventDefault();
              setActive((a) => Math.max(a - 1, 0));
            } else if (e.key === "Enter" && results[active]) {
              go(results[active].href);
            } else if (q === "" && /^[1-9]$/.test(e.key)) {
              // Type a section number (§1, §2, …) to jump straight there.
              const dest = dests.find((d) => d.hint === `§${e.key}`);
              if (dest) {
                e.preventDefault();
                go(dest.href);
              }
            }
          }}
          placeholder="Jump to…"
          className="w-full border-b border-border bg-transparent px-4 py-3.5 font-mono text-[14px] outline-none"
        />
        <ul className="max-h-[50vh] overflow-y-auto p-2">
          {results.map((d, i) => (
            <li key={d.href}>
              <button
                onMouseEnter={() => setActive(i)}
                onClick={() => go(d.href)}
                className={`flex w-full items-center justify-between rounded-lg px-3 py-2.5 text-left text-[14px] ${
                  i === active ? "bg-hl text-primary-ink" : ""
                }`}
              >
                {d.label}
                <span className="font-mono text-[11px] text-muted">{d.hint}</span>
              </button>
            </li>
          ))}
          {results.length === 0 && (
            <li className="px-3 py-2.5 font-mono text-[13px] text-muted">
              No matches
            </li>
          )}
        </ul>
      </div>
    </div>
  );
}
