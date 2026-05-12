# Portfolio

Personal portfolio site built with Django 5.2 and Wagtail 6. Manages CV data (education, experience, skills) via Django admin and blog/portfolio project pages via the Wagtail CMS editor.

## Tech Stack

- **Backend:** Django 5.2, Wagtail 6, PostgreSQL
- **Frontend:** Bootstrap 5, AOS, Typed.js (no build step)
- **Server:** Gunicorn + Nginx, WhiteNoise for static files
- **Container:** Docker + Docker Compose

## Docs

- [Architecture](docs/architecture.md) — app structure, models, URL routing, block types
- [Maintainability](docs/maintainability.md) — known issues, patterns to follow, upgrade notes

## Local Development

**Prerequisites:** Docker + Docker Compose

```bash
cp .env.example .env
# edit .env with your local values
docker compose -f docker-compose.dev.yml up
```

The app will be available at `http://localhost`. Wagtail admin at `/cms/`, Django admin at `/admin/`.

On first run, create a superuser:

```bash
docker compose -f docker-compose.dev.yml exec web python manage.py createsuperuser
```

To run without Docker (requires a local PostgreSQL instance):

```bash
pip install -r requirements.txt
python manage.py migrate        # uses portfolio.settings.dev by default
python manage.py runserver
```

## Production (VPS / Docker Compose)

```bash
cp .env.prod.example .env.prod
# fill in real values — never commit .env.prod
docker compose -f docker-compose.prod.yml up -d
```

Key differences from dev:
- No code volume mount — code is baked into the image
- Uses `portfolio.settings.prod` (requires `DJANGO_SECRET_KEY`, errors loudly if missing)
- `restart: unless-stopped` on all services
- WhiteNoise compressed static file storage

For Kubernetes, TLS is terminated by Cloudflare + the cluster ingress; the app only needs to expose HTTP internally.

## Environment Variables

| Variable | Description |
|---|---|
| `DJANGO_SETTINGS_MODULE` | `portfolio.settings.dev` or `portfolio.settings.prod` (Dockerfile sets prod by default) |
| `DJANGO_SECRET_KEY` | Required in prod — keep out of version control |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated allowed host names (prod) |
| `CSRF_TRUSTED_ORIGINS` | Comma-separated trusted origins, e.g. `https://example.com` (prod) |
| `POSTGRES_HOST` | Database host |
| `POSTGRES_PORT` | Database port (default `5432`) |
| `POSTGRES_DB` | Database name |
| `POSTGRES_USER` | Database user |
| `POSTGRES_PASSWORD` | Database password |
| `APP_HOST` | Gunicorn bind host (default `0.0.0.0`) |
| `APP_PORT` | Gunicorn bind port (default `8000`) |

## Container / Deployment

**Image:** `hydrodog11/portfolio:1.1` — internal port `8000`

At startup the container runs:
1. `python manage.py migrate`
2. `python manage.py collectstatic --noinput`
3. `gunicorn portfolio.wsgi:application --bind ${APP_HOST}:${APP_PORT}`

The database must be reachable before the container starts. Migrations run automatically, so **single-replica deployments are recommended** unless you coordinate migrations externally.

**Media uploads** require a persistent volume mounted at `/app/media` or an external object store (S3/MinIO). Without it, uploads are lost on container restart.

**Kubernetes:** inject configuration via Secrets and ConfigMaps; handle TLS/ingress externally.
