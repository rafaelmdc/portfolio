"use client";

import { useEffect, useRef } from "react";

/**
 * Soft animated hero backdrop: a faint "matrix" rain of DNA bases (A/C/G/T)
 * over a slowly drifting double-helix. Theme-aware (reads CSS vars), pauses for
 * prefers-reduced-motion, and stops when scrolled out of view. Purely
 * decorative — pointer-events-none, low opacity, sits behind the hero content.
 */
const BASES = "ACGT";

export default function HeroBackground() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    // Resolve theme colors from CSS custom properties (re-read on theme change).
    let bg = "#121218";
    let accent = "#7c6cf0";
    const readColors = () => {
      const cs = getComputedStyle(document.documentElement);
      bg = cs.getPropertyValue("--bg").trim() || bg;
      accent = (cs.getPropertyValue("--primary").trim() || accent);
    };
    readColors();
    const themeObserver = new MutationObserver(readColors);
    themeObserver.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ["data-theme"],
    });

    const FONT = 15; // px, glyph size + vertical fall step
    let w = 0;
    let h = 0;
    let cols = 0;
    let cell = FONT; // horizontal spacing between streams
    let drops: number[] = [];
    let dpr = 1;

    const resize = () => {
      const rect = canvas.getBoundingClientRect();
      w = rect.width;
      h = rect.height;
      dpr = Math.min(window.devicePixelRatio || 1, 2);
      canvas.width = Math.floor(w * dpr);
      canvas.height = Math.floor(h * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      // Space streams further apart on narrow screens so it doesn't clutter.
      cell = w < 540 ? 52 : w < 900 ? 36 : 22;
      cols = Math.ceil(w / cell);
      drops = Array.from({ length: cols }, () => Math.random() * -h);
      ctx.clearRect(0, 0, w, h);
    };
    resize();
    window.addEventListener("resize", resize);

    let helixPhase = 0;

    // Faint double-helix sweeping across, drawn behind the rain.
    const drawHelix = () => {
      const midY = h * 0.5;
      // Narrow screens get fewer turns (lower frequency) and a shorter wave
      // (smaller amplitude) so the helix doesn't read as a busy zigzag.
      const turns = w < 540 ? 1.1 : w < 900 ? 1.6 : 2.4;
      const ampCap = w < 540 ? 110 : w < 900 ? 170 : 220;
      const amp = Math.min(h * 0.3, ampCap);
      const step = 14;
      ctx.lineWidth = 1;
      ctx.strokeStyle = accent;
      ctx.globalAlpha = 0.22;
      for (let strand = 0; strand < 2; strand++) {
        ctx.beginPath();
        for (let x = -40; x <= w + 40; x += step) {
          const t = (x / w) * Math.PI * 2 * turns + helixPhase + strand * Math.PI;
          const y = midY + Math.sin(t) * amp;
          if (x === -40) ctx.moveTo(x, y);
          else ctx.lineTo(x, y);
        }
        ctx.stroke();
      }
      // Rungs connecting the two strands.
      ctx.globalAlpha = 0.12;
      for (let x = -40; x <= w + 40; x += step * 2) {
        const t = (x / w) * Math.PI * 2 * turns + helixPhase;
        const y1 = midY + Math.sin(t) * amp;
        const y2 = midY + Math.sin(t + Math.PI) * amp;
        ctx.beginPath();
        ctx.moveTo(x, y1);
        ctx.lineTo(x, y2);
        ctx.stroke();
      }
      ctx.globalAlpha = 1;
    };

    const drawRain = () => {
      ctx.font = `${FONT - 2}px var(--font-jetbrains), monospace`;
      ctx.textBaseline = "top";
      for (let i = 0; i < cols; i++) {
        const x = i * cell;
        const y = drops[i];
        const ch = BASES[(Math.random() * BASES.length) | 0];
        // Soft glyphs; the translucent bg wash creates the fading trail.
        ctx.fillStyle = accent;
        ctx.globalAlpha = 0.6;
        ctx.fillText(ch, x, y);
        ctx.globalAlpha = 1;
        drops[i] += FONT;
        if (drops[i] > h && Math.random() > 0.975) drops[i] = Math.random() * -120;
      }
    };

    let raf = 0;
    let last = 0;
    let running = true;

    const frame = (ts: number) => {
      if (!running) return;
      // ~14fps cadence keeps it slow + soft (and cheap).
      if (ts - last > 70) {
        last = ts;
        // Translucent wash over the whole canvas = fading trails.
        ctx.globalAlpha = 0.14;
        ctx.fillStyle = bg;
        ctx.fillRect(0, 0, w, h);
        ctx.globalAlpha = 1;
        helixPhase += 0.012;
        drawHelix();
        drawRain();
      }
      raf = requestAnimationFrame(frame);
    };

    if (reduce) {
      // Static, very faint helix only.
      ctx.fillStyle = bg;
      ctx.fillRect(0, 0, w, h);
      drawHelix();
    } else {
      raf = requestAnimationFrame(frame);
    }

    // Pause when the hero scrolls offscreen.
    const io = new IntersectionObserver(
      ([entry]) => {
        const visible = entry.isIntersecting;
        if (visible && !running && !reduce) {
          running = true;
          raf = requestAnimationFrame(frame);
        } else if (!visible) {
          running = false;
          cancelAnimationFrame(raf);
        }
      },
      { threshold: 0 },
    );
    io.observe(canvas);

    return () => {
      running = false;
      cancelAnimationFrame(raf);
      window.removeEventListener("resize", resize);
      themeObserver.disconnect();
      io.disconnect();
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      aria-hidden
      className="pointer-events-none absolute inset-0 h-full w-full opacity-[0.5] [mask-image:radial-gradient(120%_100%_at_70%_40%,#000_30%,transparent_85%)]"
    />
  );
}
