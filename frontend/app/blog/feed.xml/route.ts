import { getBlogPosts } from "@/lib/api";

const SITE_URL = (process.env.SITE_URL || "http://localhost:8000").replace(/\/$/, "");

// Built at request time against the backend (content changes without a redeploy).
export const dynamic = "force-dynamic";

const esc = (s: string) =>
  s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

export async function GET() {
  const posts = await getBlogPosts();
  const updated = posts[0]?.date
    ? new Date(posts[0].date).toUTCString()
    : new Date().toUTCString();

  const items = posts
    .map((p) => {
      const url = `${SITE_URL}/blog/${p.meta.slug}`;
      const pub = p.date ? new Date(p.date).toUTCString() : updated;
      const cats = p.tag_names.map((t) => `<category>${esc(t)}</category>`).join("");
      return `    <item>
      <title>${esc(p.title)}</title>
      <link>${url}</link>
      <guid isPermaLink="true">${url}</guid>
      <pubDate>${pub}</pubDate>
      ${cats}
      <description><![CDATA[${p.intro || ""}]]></description>
    </item>`;
    })
    .join("\n");

  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>Rafael Correia — Blog</title>
    <link>${SITE_URL}/blog</link>
    <atom:link href="${SITE_URL}/blog/feed.xml" rel="self" type="application/rss+xml" />
    <description>Notes on bioinformatics, code, and data.</description>
    <language>en</language>
    <lastBuildDate>${updated}</lastBuildDate>
${items}
  </channel>
</rss>`;

  return new Response(xml, {
    headers: { "Content-Type": "application/rss+xml; charset=utf-8" },
  });
}
