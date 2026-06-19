import type { MetadataRoute } from "next";
import { getBlogPosts, getProjects } from "@/lib/api";

const SITE_URL = process.env.SITE_URL || "http://localhost:8000";

// Built at request time against the backend (content changes without a redeploy).
export const dynamic = "force-dynamic";

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const [posts, projects] = await Promise.all([
    getBlogPosts().catch(() => []),
    getProjects().catch(() => []),
  ]);

  const staticPages: MetadataRoute.Sitemap = [
    { url: `${SITE_URL}/`, priority: 1 },
    { url: `${SITE_URL}/blog`, priority: 0.7 },
    { url: `${SITE_URL}/uses`, priority: 0.4 },
  ];

  const postPages: MetadataRoute.Sitemap = posts.map((p) => ({
    url: `${SITE_URL}/blog/${p.meta.slug}`,
    lastModified: p.date ? new Date(p.date) : undefined,
    priority: 0.6,
  }));

  const projectPages: MetadataRoute.Sitemap = projects.map((p) => ({
    url: `${SITE_URL}/portfolio/${p.meta.slug}`,
    lastModified: p.meta.first_published_at
      ? new Date(p.meta.first_published_at)
      : undefined,
    priority: 0.6,
  }));

  return [...staticPages, ...postPages, ...projectPages];
}
