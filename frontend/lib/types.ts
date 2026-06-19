export type ImageRendition = {
  url: string;
  width: number;
  height: number;
  // Only present on SiteBundle images (hand-built with two renditions); page
  // API renditions (cover_thumb/hero_thumb/card_thumb) expose `url` only.
  thumb?: string;
  alt: string;
};

export type SiteBundle = {
  copy: {
    about_title: string;
    about_lead: string;
    about_intro_headline: string;
    about_intro_body: string;
    about_quote: string;
    skills_title: string;
    skills_lead: string;
    hero_eyebrow: string;
    hero_headline: string;
    hero_highlight: string;
    hero_cta_primary: string;
    hero_cta_secondary: string;
    contact_headline: string;
    contact_note: string;
    about_focus: string;
  };
  stats: {
    stat_focus: boolean;
    stat_repos: boolean;
    stat_stars: boolean;
    stat_language: boolean;
    stat_followers: boolean;
    stat_commits: boolean;
    stat_publications: boolean;
    stat_honors: boolean;
    stat_building: boolean;
    stat_projects: boolean;
    stat_status: boolean;
    stat_domain: boolean;
  };
  about_extra: {
    building_since: number | null;
    projects_count: number;
    current_status: string;
    primary_domain: string;
  };
  images: {
    about_profile: ImageRendition | null;
    home_profile: ImageRendition | null;
  };
  skills: { name: string; description: string; icon: string }[];
  education: Education[];
  experience: Experience[];
  publications: { groups: PublicationGroup[]; flat: Publication[] };
  grants: Grant[];
  awards: Award[];
  languages: { name: string; level: string; level_display: string }[];
  github: GithubStats | null;
  orcid_id: string;
  has_research: boolean;
  sections: HomeSection[];
  contact: {
    email: string;
    linkedin_url: string;
    github_username: string;
    full_name: string;
    show_email: boolean;
    show_github: boolean;
    show_linkedin: boolean;
    show_blog: boolean;
  };
  cv: { enabled: boolean; url: string };
};

/* CMS-controlled homepage sections (ordered). Marker sections only carry an
   optional title override; gallery/carousel carry their own content. */
export type HomeSectionType =
  | "about"
  | "skills"
  | "timeline"
  | "work"
  | "research"
  | "contact"
  | "gallery"
  | "carousel";

export type GalleryItem = { image: ImageRendition | null; caption: string };
export type CarouselSlide = {
  image: ImageRendition | null;
  caption: string;
  link: string;
};

export type HomeSection = {
  id: string;
  type: HomeSectionType;
  value: {
    title?: string;
    intro?: string;
    autoplay?: boolean;
    items?: GalleryItem[];
    slides?: CarouselSlide[];
  };
};

export type Education = {
  title: string;
  institution: string;
  location: string;
  start_year: number;
  end_year: number | null;
  blurb: string;
};

export type Experience = {
  role: string;
  company: string;
  location: string;
  start_year: number;
  end_year: number | null;
  blurb: string;
  bullets: string[];
};

export type Publication = {
  title: string;
  authors: string;
  authors_display: string;
  venue: string;
  year: number;
  pub_type: string;
  doi: string;
  url: string;
  link: string;
  citation_count: number;
  featured: boolean;
};

export type PublicationGroup = { label: string; items: Publication[] };

export type Grant = {
  title: string;
  funder: string;
  role: string;
  amount: string;
  start_year: number | null;
  end_year: number | null;
  description: string;
  url: string;
};

export type Award = {
  title: string;
  issuer: string;
  year: number | null;
  description: string;
  url: string;
};

export type GithubStats = {
  username: string;
  public_repos: number | null;
  followers: number | null;
  total_stars: number;
  top_language: string | null;
  total_commits: number | null;
};

/* ---- Wagtail pages API ---- */
export type StreamBlock = { type: string; value: unknown; id: string };

export type PageMeta = {
  type: string;
  slug: string;
  html_url: string;
  first_published_at: string;
};

export type BlogListItem = {
  id: number;
  title: string;
  meta: PageMeta;
  intro: string;
  date: string;
  reading_time_minutes: number | null;
  hero_thumb: ImageRendition | null;
  card_thumb: ImageRendition | null;
  tag_names: string[];
};

export type BlogDetail = BlogListItem & {
  hero_image: ImageRendition | null;
  hero_caption: string;
  featured: boolean;
  body: StreamBlock[];
};

export type ProjectListItem = {
  id: number;
  title: string;
  meta: PageMeta;
  subtitle: string;
  cover_thumb: ImageRendition | null;
  card_thumb: ImageRendition | null;
  tag_names: string[];
};

export type ProjectDetail = ProjectListItem & {
  cover_image: ImageRendition | null;
  external_url: string;
  github_url: string;
  body: StreamBlock[];
};
