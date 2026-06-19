import type { NextRequest } from "next/server";

// Resolved at REQUEST time (route handlers run in the Node runtime), so the
// in-cluster backend URL comes from the container env — unlike next.config
// rewrites, whose destination is frozen at build time.
function backend(): string {
  return (
    process.env.INTERNAL_API_URL ||
    process.env.WAGTAIL_API_URL ||
    "http://localhost:3000"
  ).replace(/\/$/, "");
}

const HOP = new Set([
  "connection",
  "keep-alive",
  "proxy-authenticate",
  "proxy-authorization",
  "te",
  "trailers",
  "transfer-encoding",
  "upgrade",
  "host",
]);

/**
 * Proxy a browser request to the in-cluster backend, streaming the response
 * back. Redirects pass through verbatim (Location stays relative, so the
 * browser re-enters the proxy for the next hop, e.g. /resume -> /documents).
 */
export async function proxyTo(
  req: NextRequest,
  prefix: string,
  segments: string[],
): Promise<Response> {
  const target = `${backend()}/${prefix}/${segments.join("/")}${req.nextUrl.search}`;

  const headers = new Headers();
  req.headers.forEach((v, k) => {
    if (!HOP.has(k.toLowerCase())) headers.set(k, v);
  });

  const init: RequestInit = { method: req.method, headers, redirect: "manual" };
  if (req.method !== "GET" && req.method !== "HEAD") {
    init.body = await req.arrayBuffer();
  }

  const res = await fetch(target, init);

  const out = new Headers();
  res.headers.forEach((v, k) => {
    const key = k.toLowerCase();
    // fetch already decoded the body; let the runtime recompute length/encoding.
    if (HOP.has(key) || key === "content-encoding" || key === "content-length") return;
    out.set(k, v);
  });

  return new Response(res.body, {
    status: res.status,
    statusText: res.statusText,
    headers: out,
  });
}
