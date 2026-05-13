# Portfolio

Personal portfolio site built with Django and Wagtail. CV data such as education,
experience, skills, publications, grants, awards, languages, and site copy is
managed through Django admin; blog and portfolio project pages are managed
through Wagtail.

## Tech Stack

- **Backend:** Python 3.12, Django >=5.2,<6.0, Wagtail >=7.4,<8.0
- **Database:** PostgreSQL 16
- **Frontend:** Bootstrap 5, Bootstrap Icons, AOS, Typed.js, GLightbox, Isotope
  with no frontend build step
- **Content:** Wagtail StreamField blocks for rich text, images, embeds, code,
  callouts, galleries, sections, buttons, and PDF downloads
- **Runtime:** Gunicorn, Nginx, WhiteNoise, WeasyPrint
- **Container:** Docker and Docker Compose

## Docs

- [Architecture](docs/architecture.md) - app structure, models, URL routing, block types
- [Maintainability](docs/maintainability.md) - patterns to follow, upgrade notes, testing notes

## Local Development

### Docker

Prerequisites: Docker and Docker Compose.

```bash
cp .env.example .env
docker compose -f docker-compose.dev.yml up --build
```

With the example environment, the site is available at `http://localhost:8000`.
Use `HOST_PORT` in `.env` to change the host port. Wagtail admin is at
`/cms/`; Django admin is at `/admin/`.

On first run, create an admin user:

```bash
docker compose -f docker-compose.dev.yml exec web python manage.py createsuperuser
```

Common Makefile shortcuts:

```bash
make dev-up          # start the dev stack
make dev-up-build    # rebuild and start the dev stack
make dev-up-d        # start in the background
make dev-logs        # follow web logs
make dev-shell       # shell into the web container
make migrate         # run migrations in the web container
make migrations      # create migrations in the web container
make createsuperuser # create a Django admin user
```

### Without Docker

Prerequisites: Python 3.12, PostgreSQL, and the system libraries required by
Pillow and WeasyPrint. The Dockerfile lists the Debian packages used by the
container.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

`manage.py` defaults to `portfolio.settings.dev`. The dev settings expect
PostgreSQL on `localhost:5432` unless `POSTGRES_*` environment variables are
set.

## Content Management

- `/admin/` manages CV data, site copy, site assets, publications, grants,
  awards, languages, and skills.
- `/cms/` manages Wagtail pages for blog posts and portfolio projects.
- `/resume/` renders the HTML CV.
- `/resume/pdf/` generates a downloadable PDF with WeasyPrint.
- `/blog/feed/` and `/blog/feed/atom/` expose RSS and Atom feeds.
- `/sitemap.xml` and `/robots.txt` are served by Django.

Useful sync commands:

```bash
python manage.py sync_orcid --orcid-id 0000-0001-2345-6789
python manage.py sync_orcid --dry-run
python manage.py sync_citations --dry-run
```

`sync_orcid` can also read `ORCID_ID` and `ORCID_HIGHLIGHT_NAME` from the
environment.

## Environment Variables

| Variable | Description |
|---|---|
| `DJANGO_SETTINGS_MODULE` | `portfolio.settings.dev` or `portfolio.settings.prod`; the Docker image defaults to prod |
| `DJANGO_SECRET_KEY` | Required in production |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated host names for production |
| `CSRF_TRUSTED_ORIGINS` | Comma-separated trusted origins, for example `https://example.com` |
| `WAGTAIL_BASE_URL` | Public base URL used by Wagtail admin and generated links |
| `POSTGRES_HOST` | Database host; compose sets this to `db` |
| `POSTGRES_PORT` | Database port; defaults to `5432` |
| `POSTGRES_DB` | Database name |
| `POSTGRES_USER` | Database user |
| `POSTGRES_PASSWORD` | Database password |
| `APP_HOST` | Gunicorn bind host inside the container; defaults to `0.0.0.0` |
| `APP_PORT` | Gunicorn bind port inside the container; keep at `8000` unless `nginx/default.conf` is updated too |
| `HOST_PORT` | Development host port mapped to Nginx; defaults to `8000` in `.env.example` |
| `IMAGE_TAG` | Production compose image tag; defaults to `latest` |
| `ORCID_ID` | Optional public ORCID iD for `sync_orcid` |
| `ORCID_HIGHLIGHT_NAME` | Optional author name to bold in publication lists |

Use `.env.example` for local Docker development and `.env.prod.example` for
production compose deployments. Do not commit real `.env` or `.env.prod` files.

## Deployment

### Image Publishing

Pushing to `main` triggers `.github/workflows/docker-publish.yml`, which builds
and pushes:

- `hydrodog11/portfolio:latest`
- `hydrodog11/portfolio:<github-sha>`

Required GitHub Actions secrets:

| Secret | Value |
|---|---|
| `DOCKERHUB_USERNAME` | Docker Hub username |
| `DOCKERHUB_TOKEN` | Docker Hub access token |

To build and push manually from the current checkout:

```bash
make release
```

The manual Makefile release publishes:

- `hydrodog11/portfolio:latest`
- `hydrodog11/portfolio:<short-git-sha>`

### Production Compose Smoke Test

```bash
cp .env.prod.example .env.prod
# fill in real values
make prod-up
```

`docker-compose.prod.yml` pulls `hydrodog11/portfolio:${IMAGE_TAG:-latest}`,
starts PostgreSQL, runs the app behind Nginx, and exposes HTTP on host port
`80`.

## Container Behavior

The image listens on internal port `8000` by default. At startup it runs:

1. `python manage.py migrate`
2. `python manage.py collectstatic --noinput`
3. `gunicorn portfolio.wsgi:application --bind ${APP_HOST}:${APP_PORT}`

Because migrations run automatically at app startup, single-replica deployments
are recommended unless migrations are coordinated externally.

Media uploads require persistent storage mounted at `/app/media` or an external
object store. Without persistent media storage, uploaded images and documents are
lost when the container is replaced.

TLS is expected to terminate outside the app, for example at Cloudflare or an
ingress proxy. Production settings trust `X-Forwarded-Proto` and enable secure
cookies and HSTS.

## Tests

Run tests inside the Docker dev stack:

```bash
docker compose -f docker-compose.dev.yml exec web python manage.py test
```

Or, with a local Python/PostgreSQL setup:

```bash
python manage.py test
```
