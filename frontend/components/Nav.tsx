import Link from "next/link";
import ThemeToggle from "./ThemeToggle";

const LINKS = [
  { href: "#about", n: "§1", label: "about" },
  { href: "#skills", n: "§2", label: "skills" },
  { href: "#timeline", n: "§3", label: "timeline" },
  { href: "#work", n: "§4", label: "work" },
];

export default function Nav({ hasResearch }: { hasResearch: boolean }) {
  return (
    <header className="sticky top-0 z-50 border-b border-border bg-bg/80 backdrop-blur-md backdrop-saturate-150">
      <nav className="mx-auto flex h-[62px] max-w-5xl items-center gap-7 px-7">
        <span className="font-mono text-[13px] font-medium">
          rafael<span className="text-primary">.correia</span>()
        </span>
        <div className="ml-auto hidden gap-[22px] md:flex">
          {LINKS.map((l) => (
            <a
              key={l.href}
              href={l.href}
              className="font-mono text-[12.5px] text-muted transition hover:text-ink"
            >
              <span className="text-primary/70">{l.n}</span> {l.label}
            </a>
          ))}
          {hasResearch && (
            <a
              href="#research"
              className="font-mono text-[12.5px] text-muted transition hover:text-ink"
            >
              <span className="text-primary/70">§5</span> research
            </a>
          )}
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
        </div>
      </nav>
    </header>
  );
}
