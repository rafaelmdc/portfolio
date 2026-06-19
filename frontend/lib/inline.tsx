import React from "react";

// Minimal inline-markdown renderer for plain-text CMS fields that may contain
// **bold**, *italic*/_italic_, `code`, and [text](url). These fields are not
// RichText, so the raw markers would otherwise render literally.
const TOKEN = /(\*\*[^*]+\*\*|\*[^*]+\*|_[^_]+_|`[^`]+`|\[[^\]]+\]\([^)]+\))/g;

export function inline(text: string): React.ReactNode {
  if (!text) return text;
  const parts = text.split(TOKEN);
  return parts.map((part, i) => {
    if (part.startsWith("**") && part.endsWith("**"))
      return <strong key={i}>{part.slice(2, -2)}</strong>;
    if (part.startsWith("*") && part.endsWith("*"))
      return <em key={i}>{part.slice(1, -1)}</em>;
    if (part.startsWith("_") && part.endsWith("_"))
      return <em key={i}>{part.slice(1, -1)}</em>;
    if (part.startsWith("`") && part.endsWith("`"))
      return (
        <code key={i} className="rounded bg-hl px-1 py-0.5 font-mono text-[0.9em]">
          {part.slice(1, -1)}
        </code>
      );
    const link = part.match(/^\[([^\]]+)\]\(([^)]+)\)$/);
    if (link)
      return (
        <a
          key={i}
          href={link[2]}
          target="_blank"
          rel="noopener noreferrer"
          className="text-primary-ink underline underline-offset-2"
        >
          {link[1]}
        </a>
      );
    return part;
  });
}
