"use client";

import { useEffect, useMemo, useState } from "react";

type Dest = { label: string; hint: string; href: string };

const DESTS: Dest[] = [
  { label: "Home", hint: "top", href: "/" },
  { label: "About", hint: "§1", href: "/#about" },
  { label: "Skills", hint: "§2", href: "/#skills" },
  { label: "Timeline", hint: "§3", href: "/#timeline" },
  { label: "Work", hint: "§4", href: "/#work" },
  { label: "Research", hint: "§5", href: "/#research" },
  { label: "Contact", hint: "§", href: "/#contact" },
  { label: "Blog", hint: "↗", href: "/blog" },
];

export default function CommandPalette() {
  const [open, setOpen] = useState(false);
  const [q, setQ] = useState("");
  const [active, setActive] = useState(0);

  const results = useMemo(() => {
    const s = q.trim().toLowerCase();
    return s ? DESTS.filter((d) => d.label.toLowerCase().includes(s)) : DESTS;
  }, [q]);

  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setOpen((o) => !o);
      } else if (e.key === "Escape") {
        setOpen(false);
      }
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  useEffect(() => {
    if (open) {
      setQ("");
      setActive(0);
    }
  }, [open]);

  if (!open) return null;

  function go(href: string) {
    setOpen(false);
    window.location.href = href;
  }

  return (
    <div
      className="fixed inset-0 z-[100] flex items-start justify-center bg-black/40 pt-[18vh]"
      onClick={() => setOpen(false)}
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
