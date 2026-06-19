import Link from "next/link";
import ThemeToggle from "./ThemeToggle";

export default function InnerHeader() {
  return (
    <header className="sticky top-0 z-50 border-b border-border bg-bg/80 backdrop-blur-md backdrop-saturate-150">
      <nav className="mx-auto flex h-[62px] max-w-5xl items-center gap-7 px-7">
        <Link href="/" className="font-mono text-[13px] font-medium">
          rafael<span className="text-primary">.correia</span>()
        </Link>
        <div className="ml-auto flex items-center gap-5">
          <Link
            href="/#work"
            className="font-mono text-[12.5px] text-muted transition hover:text-ink"
          >
            ← back
          </Link>
          <Link
            href="/blog"
            className="font-mono text-[12.5px] text-muted transition hover:text-ink"
          >
            blog
          </Link>
          <ThemeToggle />
        </div>
      </nav>
    </header>
  );
}
