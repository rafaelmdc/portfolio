import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Self-contained server bundle for a small production Docker image.
  output: "standalone",

  // Browser-facing backend paths (/api, /media, /documents, /resume) are
  // proxied to the in-cluster backend by Route Handlers (app/*/[...path]/route.ts),
  // NOT next.config rewrites — rewrite destinations are frozen at build time, so
  // they'd bake in localhost. Route Handlers read INTERNAL_API_URL at request
  // time. /cms and the rest of the Django surface are intentionally not proxied.
};

export default nextConfig;
