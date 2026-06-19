import type {
  SiteBundle,
  BlogListItem,
  BlogDetail,
  ProjectListItem,
  ProjectDetail,
} from "./types";

// Server-side (SSR) base URL for the headless Wagtail backend. In production
// this is an internal/in-cluster address that is NOT exposed to the public
// internet; the browser never uses it (see mediaUrl + next.config rewrites).
const INTERNAL_API_URL = (
  process.env.INTERNAL_API_URL ||
  process.env.WAGTAIL_API_URL ||
  "http://localhost:3000"
).replace(/\/$/, "");

const REVALIDATE = 300; // seconds (ISR)

/**
 * Browser-facing asset URL (images, CV, documents). These are served
 * same-origin and proxied to the backend by next.config `rewrites()`, so a
 * backend-relative path (e.g. "/media/…") is returned unchanged. Absolute
 * URLs (external) pass through.
 */
export function mediaUrl(path: string | null | undefined): string {
  if (!path) return "";
  if (path.startsWith("http")) return path;
  return path;
}

async function getJSON<T>(path: string): Promise<T> {
  // Server-side fetch goes straight to the internal backend (no proxy hop).
  const res = await fetch(`${INTERNAL_API_URL}${path}`, {
    next: { revalidate: REVALIDATE },
  });
  if (!res.ok) {
    throw new Error(`API ${path} -> ${res.status}`);
  }
  return res.json() as Promise<T>;
}

export function getSiteBundle(): Promise<SiteBundle> {
  return getJSON<SiteBundle>("/api/v2/site/");
}

const BLOG_FIELDS = "intro,date,hero_thumb,tag_names,reading_time_minutes";
const BLOG_DETAIL_FIELDS =
  "intro,date,featured,hero_image,hero_caption,reading_time_minutes,tag_names,body";
const PROJECT_FIELDS = "subtitle,cover_thumb,tag_names";
const PROJECT_DETAIL_FIELDS =
  "subtitle,cover_image,external_url,github_url,tag_names,body";

type ApiList<T> = { meta: { total_count: number }; items: T[] };

export async function getBlogPosts(): Promise<BlogListItem[]> {
  const data = await getJSON<ApiList<BlogListItem>>(
    `/api/v2/pages/?type=cms.BlogPage&fields=${BLOG_FIELDS}&order=-date&limit=50`,
  );
  return data.items;
}

export async function getBlogPost(slug: string): Promise<BlogDetail | null> {
  const data = await getJSON<ApiList<BlogDetail>>(
    `/api/v2/pages/?type=cms.BlogPage&slug=${encodeURIComponent(slug)}&fields=${BLOG_DETAIL_FIELDS}`,
  );
  return data.items[0] ?? null;
}

export async function getProjects(): Promise<ProjectListItem[]> {
  const data = await getJSON<ApiList<ProjectListItem>>(
    `/api/v2/pages/?type=cms.PortfolioProjectPage&fields=${PROJECT_FIELDS}&limit=50`,
  );
  return data.items;
}

export async function getProject(slug: string): Promise<ProjectDetail | null> {
  const data = await getJSON<ApiList<ProjectDetail>>(
    `/api/v2/pages/?type=cms.PortfolioProjectPage&slug=${encodeURIComponent(slug)}&fields=${PROJECT_DETAIL_FIELDS}`,
  );
  return data.items[0] ?? null;
}

// Detail fields requested per page type when rendering a CMS draft preview.
const HOME_DETAIL_FIELDS = "intro,sections";
const PREVIEW_FIELDS: Record<string, string> = {
  "cms.blogpage": BLOG_DETAIL_FIELDS,
  "cms.portfolioprojectpage": PROJECT_DETAIL_FIELDS,
  "cms.homepage": HOME_DETAIL_FIELDS,
};

/**
 * Fetch an unsaved DRAFT page for the CMS preview. The backend's
 * /api/v2/page_preview/ endpoint reconstructs the edited page from a signed
 * token (see wagtail_headless_preview). Never cached — drafts change per edit.
 */
export async function getPreview(
  contentType: string,
  token: string,
): Promise<Record<string, unknown> | null> {
  const fields = PREVIEW_FIELDS[contentType.toLowerCase()] ?? "";
  const qs = new URLSearchParams({ content_type: contentType, token });
  if (fields) qs.set("fields", fields);
  const res = await fetch(`${INTERNAL_API_URL}/api/v2/page_preview/?${qs}`, {
    cache: "no-store",
  });
  if (!res.ok) return null;
  return res.json() as Promise<Record<string, unknown>>;
}
