import type { NextRequest } from "next/server";
import { proxyTo } from "@/lib/proxy";

export const dynamic = "force-dynamic";

type Ctx = { params: Promise<{ path: string[] }> };

export async function GET(req: NextRequest, ctx: Ctx) {
  return proxyTo(req, "media", (await ctx.params).path);
}

export const HEAD = GET;
