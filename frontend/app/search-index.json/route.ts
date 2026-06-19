import { getBlogPosts, getProjects } from "@/lib/api";

// Lightweight client-search index (titles + slugs + tags) for the command
// palette. Built at request time against the backend.
export const dynamic = "force-dynamic";

export type SearchEntry = {
  title: string;
  href: string;
  type: "post" | "project";
  tags: string[];
};

export async function GET() {
  const [posts, projects] = await Promise.all([
    getBlogPosts().catch(() => []),
    getProjects().catch(() => []),
  ]);
  const entries: SearchEntry[] = [
    ...posts.map((p) => ({
      title: p.title,
      href: `/blog/${p.meta.slug}`,
      type: "post" as const,
      tags: p.tag_names,
    })),
    ...projects.map((p) => ({
      title: p.title,
      href: `/portfolio/${p.meta.slug}`,
      type: "project" as const,
      tags: p.tag_names,
    })),
  ];
  return Response.json(entries);
}
