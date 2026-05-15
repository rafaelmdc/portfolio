IMAGE := hydrodog11/portfolio
SHA   := $(shell git rev-parse --short HEAD)
DC    := docker compose -f docker-compose.dev.yml
MANAGE := $(DC) exec web python manage.py

.PHONY: build push release \
        dev-up dev-up-build dev-up-d dev-down dev-logs dev-shell dev-restart \
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
