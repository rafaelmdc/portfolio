"use client";

export default function ThemeToggle() {
  function toggle() {
    const cur =
      document.documentElement.getAttribute("data-theme") || "light";
    const next = cur === "light" ? "dark" : "light";
    document.documentElement.setAttribute("data-theme", next);
    try {
      localStorage.setItem("theme", next);
    } catch {}
  }

  return (
    <button
      onClick={toggle}
      aria-label="Toggle colour theme"
      className="grid h-[34px] w-[34px] place-items-center rounded-[9px] border border-border bg-surface text-[15px] transition hover:border-primary"
    >
      ◐
    </button>
  );
}
