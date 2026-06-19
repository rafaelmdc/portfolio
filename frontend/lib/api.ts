import type {
  SiteBundle,
  BlogListItem,
  BlogDetail,
  ProjectListItem,
  ProjectDetail,
} from "./types";

// Server-side base URL for the headless Wagtail backend.
export const API_BASE =
  process.env.WAGTAIL_API_URL?.replace(/\/$/, "") || "http://localhost:8000";

const REVALIDATE = 300; // seconds (ISR)

/** Prefix backend-relative media/rendition paths with the API origin. */
export function mediaUrl(path: string | null | undefined): string {
  if (!path) return "";
  if (path.startsWith("http")) return path;
  return `${API_BASE}${path}`;
}

async function getJSON<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
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
