"use client";

import { useState } from "react";

export default function CodeBlock({ value }: { value: Record<string, unknown> }) {
  const terminal = value.style === "terminal";
  const code = (value.code as string) || "";
  const [copied, setCopied] = useState(false);

  async function copy() {
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      setTimeout(() => setCopied(false), 1600);
    } catch {
      /* clipboard unavailable — ignore */
    }
  }

  return (
    <div
      className={`group relative my-7 overflow-hidden rounded-xl border border-border ${
        terminal ? "bg-[#16131f] text-[#e7e3f0]" : "bg-surface"
      }`}
    >
      {Boolean(value.title || value.language) && (
        <div className="flex items-center justify-between border-b border-border/40 px-4 py-2 font-mono text-[11.5px] text-muted">
          <span>{(value.title as string) || ""}</span>
          <span>{value.language as string}</span>
        </div>
      )}
      <button
        onClick={copy}
        aria-label="Copy code"
        className="absolute right-2.5 top-2.5 z-10 rounded-md border border-border bg-bg/70 px-2 py-1 font-mono text-[11px] text-muted opacity-0 backdrop-blur transition hover:border-primary hover:text-ink focus:opacity-100 group-hover:opacity-100"
      >
        {copied ? "✓ copied" : "copy"}
      </button>
      <pre className="overflow-x-auto p-4 font-mono text-[13px] leading-[1.6]">
        <code>{code}</code>
      </pre>
    </div>
  );
}
