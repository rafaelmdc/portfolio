# Migration Plan — Headless Wagtail + React/Tailwind

Status: planning. All work happens on a feature branch; `main` auto-deploys via
Argo CD (DockerHub image built on push to `main`). Nothing reaches `main` until a
phase is working and approved.

## Target architecture

- **Next.js frontend** (App Router + TS + Tailwind), its own image/Deployment.
  - `/` — single scrollable landing page (About, Skills, Timeline, Work, Research, Contact).
  - `/blog`, `/blog/[slug]` — separate routes (SSG/ISR for SEO).
  - `/portfolio/[slug]` — project detail routes.
- **One Wagtail backend** (no more half-Django/half-Wagtail). All content edited in `/cms`.
- **Headless via Wagtail REST API**; StreamField serialized to JSON.
- **Deploy:** Argo CD on Kubernetes; Argo watches the `Rafael-Homelab` repo and pulls `latest`
  from DockerHub. Adding the frontend is a one-file manifest change — done **last**, with the
  user. Do not touch the homelab repo until the migration is otherwise complete.

## Locked decisions
- Frontend: **Next.js** (own Deployment) · package manager **pnpm**.
- Backend run/migrate locally via **docker compose (dev)** (matches prod versions).
- Model→snippet migration verified against a **prod DB dump** (user provides).
- Deployment wiring (homelab manifest) is the final phase; untouched until then.

## Design direction — "Marginalia"

Subject: Rafael Correia, **MSc Bioinformatics student** (biology ∩ data) — pipelines,
genomics, reproducible analysis. Strong research *experience* (Researcher + Research
Trainee roles, IJUP Best Poster) but no publications yet.

A precisely typeset research document, annotated with pastel highlighter accents +
margin notes + a monospace metadata layer. Pastels are the *markup*, not the mood.
Skills are color-coded by the two halves of the field (computational vs biology).

- **Type:** Fraunces (display) · Inter (body) · JetBrains Mono (metadata/citations).
- **Light palette (pastel):** paper `#F7F5FB`, ink `#1E2029`, primary violet `#6A4FBF`,
  highlighters mint `#CFEEE0` / lilac `#E0D6F7` / peach `#FCE0CF` / sky `#D3E7F8`.
- **Dark (derived):** ink `#121218`, same pastels as soft translucent glows.
- **Signature:** numbered §-sections, reference-style publications with mono `[doi]` /
  `[cited by N]` chips, and a highlighter sweep across one hero phrase on load.
- Working mockup: `design/mockup.html`.

### Adaptive content (data-driven, automatic)
- **GitHub/portfolio stats** (repos, stars, top language, projects shipped) are **always**
  shown in the About panel — the site is builder-centric by default.
- The **Research section** and the publications/citations stat rows are **additive**:
  they render **only when publications exist**, on top of (not replacing) the GitHub stats.
  Hero/About/Contact copy can shift to acknowledge research when it's present.
- **Sections render conditionally** in general — anything with no data is omitted.
- **Skills** render as centered rows.
- **Timeline** (Education + Professional Experience) is a first-class section — vertical
  line with markers, year ranges in mono, kept from the current site (user favourite).
- GitHub stats need a source: store a GitHub username in site settings and fetch via the
  GitHub API (cached server-side, or at build time) — Phase 2.

## Phase 0 — Wagtail 7.4 upgrade & baseline
- Install/lock Wagtail 7.4 LTS (requirements already pins it); migrate; smoke-test admin + pages.
- Resolve 6→7 deprecations. Snapshot DB before any consolidation.

## Phase 1 — Consolidate `main` into Wagtail
- Convert `main` models to Wagtail **snippets**, same fields (no reshaping):
  Education, Experience (+ ExperienceBullet inline), Publication, Grant, Award,
  Language, Skill.
- `SiteCopy` + `SiteAsset` → a Wagtail **site-settings singleton** ("Site content").
- Data migrations preserve all existing rows; verify counts before/after.
- Keep the LaTeX → PDF CV generator (`main.cv_pdf`); repoint at snippet data.
- Retire `main` templates, `django-ckeditor-5`, split URL routing.

## Phase 2 — API layer
- Enable `wagtail.api.v2` for pages (Blog, Portfolio, indexes); set `api_fields`
  (hero/cover renditions, intro, date, tags, body-as-JSON, links).
- Custom API for snippet/résumé data: `/api/v2/resume/` (education, experience+bullets,
  publications grouped by type, grants, awards, languages, skills, site copy/images).
- Expose `citation_count`, ORCID id, `reading_time_minutes` in the API.
- Keep `/resume/pdf/` as a direct endpoint (React links to it).
- Expose Wagtail renditions for responsive `srcset`.

## Phase 3 — Next.js + Tailwind frontend
- Scaffold Next.js (App Router) + Tailwind + pnpm; TanStack Query for client fetches.
- Build the "Marginalia" design system (tokens, type, motion primitives).
- Landing sections (each fetches its API slice): Hero, About, Skills, Work, Research, Contact.
- Blog index (featured + pagination + tag filter) and post detail.
- Portfolio project detail pages.
- **StreamField renderer**: React component per block type (~13: heading, aligned
  paragraph, image, gallery/carousel, embed, callout, code+highlight, button, divider,
  spacer, blockquote, PDF downloads, nested section), honoring all presentation controls.

## Phase 4 — SEO, feeds, deployment (LAST)
- SEO/SSR comes free with Next.js SSG/ISR for blog + project routes.
- Keep RSS/Atom feeds + sitemap server-side in Wagtail.
- Build + push the Next.js frontend image and the (consolidated) Wagtail image to DockerHub.
- Add the frontend Deployment/Service/Ingress to the homelab manifests (one-file change) and
  let Argo sync. This is the only step that touches `Rafael-Homelab/`; do it last, with the user.

## Feature additions (folded into the phases)
- **Live citation counts / ORCID badge** on publications (uses `citation_count`, `orcid_put_code`) — Phase 2/3.
- **Command palette (⌘K)** to jump to sections / posts / projects — Phase 3.
- **Dark / light toggle**, system-preference default (pastel light, derived dark) — Phase 3.
- **Per-post OG images** (auto-generated) for sharp social previews — Phase 4.
- **Publication & project filtering** by tag/type (tag infra already exists) — Phase 2/3.
- **Reading time + tag chips** on blog (model has `reading_time_minutes`) — Phase 3.
- **Featured project surfaced on the landing page**, deep-linking to the full route — Phase 3.
- **Motion system**: orchestrated hero load, scroll-reveal, View Transitions between
  routes, hover micro-interactions, scroll-progress indicator — Phase 3.
- **Quality floor (non-negotiable)**: keyboard focus, `prefers-reduced-motion`,
  Lighthouse 95+, responsive to mobile — throughout.

## Risks
1. StreamField → React rendering is the largest single chunk.
2. SPA SEO for the blog (needs the Phase 4 prerender/SSR decision).
3. Data migration of `main` models — verify no content loss.
4. Two images (frontend + backend) and the homelab manifest change land last; don't touch
   `Rafael-Homelab/` until then (Argo auto-syncs it).

## Suggested order
Phase 0 → 1 → 2 (backend consolidated, old site still works) → 3 → 4.
Site stays functional at every step; each phase is its own PR.
