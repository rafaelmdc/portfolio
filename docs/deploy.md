# Deployment (headless: Wagtail backend + Next.js frontend)

Two images, two Deployments. Argo CD watches the `Rafael-Homelab` repo and pulls
`latest` from DockerHub. **Do not edit the homelab repo until cutover** — this doc
is the reference for that final step.

## Images

| Component | Image | Build |
|-----------|-------|-------|
| Backend (Wagtail + API) | `hydrodog11/portfolio` | `make release` (root `Dockerfile`) |
| Frontend (Next.js) | `hydrodog11/portfolio-frontend` | `make frontend-release` (`frontend/Dockerfile`) |

The frontend image is a standalone Next.js server (`output: "standalone"`),
runs as non-root on **:3000**, and needs **no backend access at build time**
(all API-backed routes are `force-dynamic`, rendered at request time).

## Runtime config

Frontend container env:

- `WAGTAIL_API_URL` — public URL of the backend. Used for server-side JSON
  fetches **and** for the media/image URLs baked into the HTML (loaded by the
  browser), so it must be **publicly reachable**, not an internal-only Service
  name. e.g. `https://api.rafael.duarte-correia.pt`.

Backend env: unchanged from today (see `.env.prod.example`). Ensure CORS is not
required — the frontend fetches server-side only.

## What the API exposes (already live on this branch)

- `/api/v2/pages/` — blog & portfolio pages (StreamField as JSON, image
  renditions embedded).
- `/api/v2/site/` — landing-page bundle (copy, profile images, CV snippets,
  GitHub stats, `has_research`).
- `/api/v2/images/`, `/cms/` (admin), `/resume/pdf/`, `/blog/feed/`, `/sitemap.xml`.

## Homelab change (the FINAL step — not yet done)

Add to the portfolio app manifests in `Rafael-Homelab/kubernetes/...`:

1. A **Deployment** for `hydrodog11/portfolio-frontend:latest`
   (containerPort 3000, env `WAGTAIL_API_URL=<public backend URL>`).
2. A **Service** targeting port 3000.
3. **Ingress** routing:
   - the site root → frontend Service,
   - `/cms`, `/api`, `/media`, `/documents`, `/resume`, `/sitemap.xml`, feeds →
     backend Service (so the browser can reach media/admin/API on the public host).

Then let Argo sync. Verify, then retire the old monolith routing.

## Local full-stack smoke test

```sh
# backend
make dev-up-d                      # stack on :8000
docker compose -f docker-compose.dev.yml exec web python manage.py seed_demo

# frontend image
make frontend-build
docker run --rm --add-host=host.docker.internal:host-gateway \
  -e WAGTAIL_API_URL=http://host.docker.internal:8000 \
  -p 3200:3000 hydrodog11/portfolio-frontend:latest
# → http://localhost:3200
```
