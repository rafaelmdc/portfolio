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

The frontend is the **only** public component. It proxies the browser-facing
backend paths through itself (`next.config.ts` `rewrites()`), so the backend can
stay **in-network only** — nothing on the Django/Wagtail side is exposed to the
public internet.

Frontend container env:

- `INTERNAL_API_URL` — in-cluster URL of the backend Service, used only for
  server-side (SSR) JSON fetches. e.g. `http://portfolio-web:8000`. **Not
  public.** (`WAGTAIL_API_URL` is still honoured as a fallback.)

Proxied to the backend by the frontend (browser → frontend origin → backend):
`/api/*`, `/media/*`, `/documents/*`, `/resume/*`. Everything else on the
backend (notably `/cms/`) is **not** proxied — reach the CMS over LAN/VPN.

No CORS config needed — the browser only ever talks to the frontend origin.

## What the API exposes (already live on this branch)

- `/api/v2/pages/` — blog & portfolio pages (StreamField as JSON, image
  renditions embedded).
- `/api/v2/site/` — landing-page bundle (copy, profile images, CV snippets,
  GitHub stats, `has_research`).
- `/api/v2/images/`, `/cms/` (admin), `/resume/pdf/`, `/blog/feed/`, `/sitemap.xml`.

## Homelab change (the FINAL step — not yet done)

Add to the portfolio app manifests in `Rafael-Homelab/kubernetes/...`:

1. A **Deployment** for `hydrodog11/portfolio-frontend:latest`
   (containerPort 3000, env `INTERNAL_API_URL=http://<backend-service>:8000`).
2. A **Service** targeting port 3000.
3. **Ingress**: route the public host **entirely to the frontend Service**.
   The frontend proxies `/api`, `/media`, `/documents`, `/resume` to the backend
   internally — so the **backend Service stays cluster-internal (ClusterIP, no
   public Ingress)**. Reach `/cms/` over LAN/VPN or a port-forward.

Optionally schedule the CV refresh: a **CronJob** running
`python manage.py gen_cv` (daily or weekly) on the backend image keeps the
cached CV PDF fresh without relying on a visitor click.

Then let Argo sync. Verify, then retire the old monolith routing.

## Local full-stack smoke test

```sh
# backend
make dev-up-d                      # stack on :8000
docker compose -f docker-compose.dev.yml exec web python manage.py seed_demo

# frontend image
make frontend-build
docker run --rm --add-host=host.docker.internal:host-gateway \
  -e INTERNAL_API_URL=http://host.docker.internal:8000 \
  -p 3200:3000 hydrodog11/portfolio-frontend:latest
# → http://localhost:3200
```
