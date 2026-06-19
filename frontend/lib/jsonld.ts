import type { SiteBundle, BlogDetail, ProjectDetail } from "./types";

// Public site origin for absolute URLs (schema.org wants fully-qualified URLs).
const SITE_URL = (process.env.SITE_URL || "http://localhost:8000").replace(/\/$/, "");

const abs = (path: string) => (path.startsWith("http") ? path : `${SITE_URL}${path}`);

type Ld = Record<string, unknown>;

/** A schema.org Person built from the site bundle identity fields. */
export function personLd(bundle: SiteBundle): Ld {
  const c = bundle.contact;
  const sameAs = [
    c.github_username ? `https://github.com/${c.github_username}` : "",
    c.linkedin_url,
    bundle.orcid_id ? `https://orcid.org/${bundle.orcid_id}` : "",
  ].filter(Boolean);
  const ld: Ld = {
    "@context": "https://schema.org",
    "@type": "Person",
    name: c.full_name || "Rafael Correia",
    url: SITE_URL,
    jobTitle: c.role_title || undefined,
    description: bundle.copy.about_lead || bundle.copy.hero_headline || undefined,
    image: abs("/opengraph-image"),
  };
  if (sameAs.length) ld.sameAs = sameAs;
  if (bundle.about_extra.primary_domain) ld.knowsAbout = bundle.about_extra.primary_domain;
  return ld;
}

/** A schema.org BlogPosting for a blog detail page. */
export function articleLd(post: BlogDetail, bundle: SiteBundle): Ld {
  const url = abs(`/blog/${post.meta.slug}`);
  return {
    "@context": "https://schema.org",
    "@type": "BlogPosting",
    headline: post.title,
    description: post.intro || undefined,
    datePublished: post.date || post.meta.first_published_at || undefined,
    image: abs(`/blog/${post.meta.slug}/opengraph-image`),
    keywords: post.tag_names.length ? post.tag_names.join(", ") : undefined,
    author: { "@type": "Person", name: bundle.contact.full_name || "Rafael Correia", url: SITE_URL },
    mainEntityOfPage: { "@type": "WebPage", "@id": url },
    url,
  };
}

/** A schema.org CreativeWork for a portfolio project. */
export function creativeWorkLd(project: ProjectDetail, bundle: SiteBundle): Ld {
  const url = abs(`/portfolio/${project.meta.slug}`);
  const keywords = [...project.tech_list, ...project.tag_names];
  const ld: Ld = {
    "@context": "https://schema.org",
    "@type": project.github_url ? "SoftwareSourceCode" : "CreativeWork",
    name: project.title,
    description: project.result_metric || project.subtitle || undefined,
    datePublished: project.date || project.meta.first_published_at || undefined,
    image: abs(`/portfolio/${project.meta.slug}/opengraph-image`),
    keywords: keywords.length ? keywords.join(", ") : undefined,
    author: { "@type": "Person", name: bundle.contact.full_name || "Rafael Correia", url: SITE_URL },
    url,
  };
  if (project.github_url) ld.codeRepository = project.github_url;
  return ld;
}

/** A schema.org BreadcrumbList from an ordered [name, path] trail. */
export function breadcrumbLd(trail: [string, string][]): Ld {
  return {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: trail.map(([name, path], i) => ({
      "@type": "ListItem",
      position: i + 1,
      name,
      item: abs(path),
    })),
  };
}
