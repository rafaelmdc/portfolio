IMAGE     := hydrodog11/portfolio
FE_IMAGE  := hydrodog11/portfolio-frontend
SHA   := $(shell git rev-parse --short HEAD)
DC    := docker compose -f docker-compose.dev.yml
MANAGE := $(DC) exec web python manage.py

# Full local stack
FE_DIR     := frontend
FE_PIDFILE := /tmp/portfolio-frontend.pid
FE_LOG     := /tmp/portfolio-frontend.log
FE_PORT    := 8000
BE_PORT    := 3000

.PHONY: build push release \
        frontend-build frontend-push frontend-release \
        dev-up dev-up-build dev-up-d dev-down dev-logs dev-shell dev-restart \
        local-up local-up-build local-down local-logs frontend-dev frontend-stop \
        migrate migrations shell dbshell \
        createsuperuser \
        cv-test-pdf \
        prod-up prod-down prod-logs

# ── Docker image ────────────────────────────────────────────────
build:
	docker build -t $(IMAGE):$(SHA) -t $(IMAGE):latest .

push: build
	docker push $(IMAGE):$(SHA)
	docker push $(IMAGE):latest

release: push

# ── Frontend (Next.js) image ────────────────────────────────────
frontend-build:
	docker build -t $(FE_IMAGE):$(SHA) -t $(FE_IMAGE):latest ./frontend

frontend-push: frontend-build
	docker push $(FE_IMAGE):$(SHA)
	docker push $(FE_IMAGE):latest

frontend-release: frontend-push

# ── Dev environment ─────────────────────────────────────────────
dev-up:
	$(DC) up

dev-up-build:
	$(DC) up --build

dev-up-d:
	$(DC) up -d

dev-down:
	$(DC) down

dev-restart:
	$(DC) restart web

dev-logs:
	$(DC) logs -f web

dev-shell:
	$(DC) exec web /bin/bash

# ── Full local stack: backend containers + frontend dev server ──────
# `make local-up`  → db/web/nginx on :$(BE_PORT) + Next.js dev on :$(FE_PORT)
# `make local-down`→ stops the frontend and the whole compose stack
local-up: dev-up-d frontend-dev
	@echo ""
	@echo "  Site (frontend): http://localhost:$(FE_PORT)"
	@echo "  CMS  (backend):  http://localhost:$(BE_PORT)/cms/"
	@echo "  Frontend logs:   make local-logs   (file: $(FE_LOG))"

# Same but rebuilds the backend image first (use after dependency changes).
local-up-build: dev-up-build frontend-dev
	@echo ""
	@echo "  Site (frontend): http://localhost:$(FE_PORT)"
	@echo "  CMS  (backend):  http://localhost:$(BE_PORT)/cms/"

local-down: frontend-stop dev-down
	@echo "local stack down."

local-logs:
	@tail -f $(FE_LOG)

# Start the Next.js dev server detached, pointed at the backend. Idempotent:
# stops any prior instance first so ports don't collide. setsid runs it in its
# own process group so frontend-stop can kill the whole pnpm→next→next-server
# tree at once.
frontend-dev: frontend-stop
	@cd $(FE_DIR) && INTERNAL_API_URL=http://localhost:$(BE_PORT) PORT=$(FE_PORT) \
		setsid pnpm dev > $(FE_LOG) 2>&1 < /dev/null & echo $$! > $(FE_PIDFILE)
	@sleep 1; echo "frontend dev started (pgid $$(cat $(FE_PIDFILE))) on :$(FE_PORT)"

frontend-stop:
	-@if [ -f $(FE_PIDFILE) ]; then kill -- -$$(cat $(FE_PIDFILE)) 2>/dev/null; rm -f $(FE_PIDFILE); fi
	-@pkill -f "next dev -p $(FE_PORT)" 2>/dev/null
	@echo "frontend dev stopped."

# ── Django management ────────────────────────────────────────────
migrate:
	$(MANAGE) migrate

migrations:
	$(MANAGE) makemigrations

shell:
	$(MANAGE) shell

dbshell:
	$(MANAGE) dbshell

createsuperuser:
	$(MANAGE) createsuperuser

cv-test-pdf:
	$(MANAGE) gen_test_cv --output /app/test_cv.pdf
	@echo "→ test_cv.pdf written to repo root"

# ── Production ──────────────────────────────────────────────────
prod-up:
	docker compose -f docker-compose.prod.yml pull
	docker compose -f docker-compose.prod.yml up -d

prod-down:
	docker compose -f docker-compose.prod.yml down

prod-logs:
	docker compose -f docker-compose.prod.yml logs -f web
