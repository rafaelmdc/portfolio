IMAGE := hydrodog11/portfolio
SHA   := $(shell git rev-parse --short HEAD)

.PHONY: build push release dev-up dev-down prod-up prod-down

build:
	docker build -t $(IMAGE):$(SHA) -t $(IMAGE):latest .

push: build
	docker push $(IMAGE):$(SHA)
	docker push $(IMAGE):latest

# Build, tag, and push — same as what CI does
release: push

dev-up:
	docker compose -f docker-compose.dev.yml up

dev-down:
	docker compose -f docker-compose.dev.yml down

prod-up:
	docker compose -f docker-compose.prod.yml pull
	docker compose -f docker-compose.prod.yml up -d

prod-down:
	docker compose -f docker-compose.prod.yml down
