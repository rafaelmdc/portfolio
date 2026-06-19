"use client";

import { useState } from "react";
import { mediaUrl } from "@/lib/api";

/**
 * Blur-up image: paints the tiny LQIP rendition instantly as a background,
 * then fades the full image in on load. Falls back to a plain image (or the
 * gradient set by the parent) when no LQIP is available.
 */
export default function Media({
  src,
  lqip,
  alt,
  width,
  height,
  className = "",
  imgClassName = "",
}: {
  src: string;
  lqip?: string | null;
  alt: string;
  width?: number;
  height?: number;
  className?: string;
  imgClassName?: string;
}) {
  const [loaded, setLoaded] = useState(false);
  return (
    <div
      className={`relative overflow-hidden ${className}`}
      style={
        lqip
          ? {
              backgroundImage: `url(${mediaUrl(lqip)})`,
              backgroundSize: "cover",
              backgroundPosition: "center",
            }
          : undefined
      }
    >
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img
        src={mediaUrl(src)}
        alt={alt}
        width={width}
        height={height}
        loading="lazy"
        onLoad={() => setLoaded(true)}
        className={`${imgClassName} transition-opacity duration-700 ${
          loaded ? "opacity-100" : "opacity-0"
        }`}
      />
    </div>
  );
}
