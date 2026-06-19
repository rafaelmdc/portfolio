import type { MetadataRoute } from "next";

const SITE_URL = process.env.SITE_URL || "http://localhost:8000";

export default function robots(): MetadataRoute.Robots {
  return {
    // Allow crawling everything except the CMS draft-preview route.
    rules: { userAgent: "*", allow: "/", disallow: "/preview" },
    sitemap: `${SITE_URL}/sitemap.xml`,
  };
}
