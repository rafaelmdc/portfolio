import type { NextRequest } from "next/server";
import { proxyTo } from "@/lib/proxy";

export const dynamic = "force-dynamic";

type Ctx = { params: Promise<{ path: string[] }> };

// /resume/pdf returns a 302 to /documents/<id>/<file>; proxyTo passes the
// redirect through with its relative Location, so the browser re-enters the
// /documents route handler for the actual file.
export async function GET(req: NextRequest, ctx: Ctx) {
  return proxyTo(req, "resume", (await ctx.params).path);
}

export const HEAD = GET;
