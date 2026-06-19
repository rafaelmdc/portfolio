import type { NextConfig } from "next";

// Internal/in-cluster backend address. The browser never sees this — it only
// ever talks to the frontend origin, which proxies these paths to the backend.
// Set INTERNAL_API_URL in production (e.g. http://portfolio-web:8000).
const INTERNAL_API_URL = (
  process.env.INTERNAL_API_URL ||
  process.env.WAGTAIL_API_URL ||
  "http://localhost:3000"
).replace(/\/$/, "");

const nextConfig: NextConfig = {
  // Self-contained server bundle for a small production Docker image.
  output: "standalone",

  // Proxy browser-facing backend paths (API, media, documents, CV) through the
  // frontend so the backend can stay in-network only. /cms and the rest of the
  // Django surface are intentionally NOT proxied.
  async rewrites() {
    return [
      { source: "/api/:path*", destination: `${INTERNAL_API_URL}/api/:path*` },
      { source: "/media/:path*", destination: `${INTERNAL_API_URL}/media/:path*` },
      { source: "/documents/:path*", destination: `${INTERNAL_API_URL}/documents/:path*` },
      { source: "/resume/:path*", destination: `${INTERNAL_API_URL}/resume/:path*` },
    ];
  },
};

export default nextConfig;
