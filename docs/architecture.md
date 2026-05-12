# Architecture

## Overview

This is a Django 5.2 + Wagtail 6 portfolio site served via Gunicorn behind Nginx. It has two distinct content systems that exist in parallel:

- **`main` app** — traditional Django views and admin; manages CV data (education, experience, skills) and static site copy/assets
- **`cms` app** — Wagtail CMS; manages blog posts and portfolio projects with a flexible block-based editor

The two systems share the same database and templates but operate independently. The home page, about, resume, and contact routes come from `main`. Blog and portfolio project pages come from Wagtail's page tree.

---

## Directory Layout

```
portfolio/          # Django project package (settings, root urls, wsgi)
main/               # CV data app — views, models, admin, signals, template tags
cms/                # Wagtail CMS app — page models, blocks, signals
nginx/              # Nginx reverse proxy config
staticfiles/        # collectstatic output (generated, not committed)
media/              # user uploads at runtime (not committed)
```

---

## Apps

### `main`

Handles everything that isn't CMS content.

**Models:**
| Model | Purpose |
|---|---|
| `Education` | Education entries; ordered by `order` field then year |
| `Experience` | Work history; has related `ExperienceBullet` rows |
| `ExperienceBullet` | Bullet points under an Experience entry |
| `Skill` | Skills with name, optional Bootstrap icon, active flag |
| `SiteCopy` | Key-value store for editable text snippets (about blurb, etc.) |
| `SiteAsset` | Key-value store for images (profile photos); enforces one active per key |
| `Timestamped` | Abstract base adding `created_at` / `updated_at` |

**Views:** `index`, `about`, `resume`, `contact` — each renders a single template with queryset context.

**Signals (`main/signals.py`):** Clean up old image files on `SiteAsset` update or delete.

**Template tags (`main/templatetags/`):**
- `|markdownify` — render Markdown to sanitized HTML (Bleach allowlist)
- `|bootstrapify` — post-process CKEditor HTML: adds Bootstrap table/image classes, wraps iframes in aspect-ratio containers

### `cms`

Wagtail page tree for dynamic content.

**Page hierarchy:**
```
HomePage (max 1)
├── BlogIndexPage         — paginated blog listing; routable tag filter at /tag/<slug>/
│   └── BlogPage          — individual post; date, read time, hero image, tags, StreamField body
└── PortfolioIndexPage    — project listing; routable tag filter
    └── PortfolioProjectPage — individual project; cover image, external/GitHub URLs, StreamField body
```

**StreamField blocks (defined in `cms/blocks.py`):**

| Block | Description |
|---|---|
| `HeadingBlock` | h2/h3/h4 with configurable level |
| `RichTextBlock` | Wagtail rich text (bold, italic, links, lists, blockquote, code) |
| `PrettyImageBlock` | Image with caption, alignment, aspect ratio, shadow, optional link |
| `PrettyEmbedBlock` | YouTube/media embed with caption and width options |
| `CalloutBlock` | Info/tip/warn/note callout box |
| `CodeBlock` | Code snippet with language selector |
| `ButtonBlock` | CTA button with text, URL, and variant |
| `DividerBlock` | `<hr>` |
| `SpacerBlock` | Vertical spacing (sm/md/lg) |
| `GalleryBlock` | 2- or 3-column image grid |
| `PdfDownloadsBlock` | 1–4 downloadable PDFs with labels |
| `SectionBlock` | Container with optional background (none/soft/contrast); accepts inner blocks |

**Signals (`cms/signals.py`):** Validate document uploads on Wagtail `Document` save — whitelist extensions (pdf, docx, txt, xlsx, pptx), max 10 MB.

---

## URL Routing

```
/                   → main.urls (home page)
/about/             → main.urls
/resume/            → main.urls
/contact/           → main.urls
/admin/             → Django admin
/cms/               → Wagtail admin
/documents/         → Wagtail document serving
/media/<path>       → media file serving
/*                  → Wagtail catch-all (serves CMS pages by slug)
```

The Wagtail catch-all is last in `portfolio/urls.py`, so `/about/` etc. are always handled by Django views.

---

## Frontend

Bootstrap 5 + custom CSS in `main/static/assets/css/main.css`. No build step — vendor libraries are checked in under `main/static/assets/vendor/`. Dark mode is set by default via `data-bs-theme="dark"` on `<html>`.

Notable vendor libs: AOS (scroll animations), Typed.js (hero text animation), GLightbox (image lightbox), Isotope (portfolio filtering), Bootstrap Icons.

---

## Infrastructure

```
Nginx  →  Gunicorn (Django)  →  PostgreSQL
            ↓
         WhiteNoise (static files)
```

`docker-compose.yml` runs three services: `web` (Django), `db` (PostgreSQL), `nginx`. At container startup, `manage.py migrate` and `collectstatic` run before Gunicorn starts.

Static files are served by WhiteNoise middleware in production (no Nginx route needed for `/static/`). Media files are served by Nginx directly and require a persistent volume or external object store.
