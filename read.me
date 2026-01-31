# PORTFOLIO – DJANGO / WAGTAIL CONTAINER IMAGE

## Image
hydrodog11/portfolio:1.1

## Internal Port
8000

## GENERAL DESCRIPTION

This Docker image packages a Django + Wagtail application intended to run in containerized environments, including Kubernetes.

The image executes database migrations and static file collection at container startup.

The image contains:
- Application code
- Python dependencies
- Startup logic for migrations and static files

The image does NOT contain:
- Secrets
- A database
- Persistent runtime data

All configuration is provided at runtime via environment variables (Kubernetes Secrets / ConfigMaps).

## CONTAINER STARTUP BEHAVIOR

When the container starts, it executes the following sequence:

1. python manage.py migrate  
2. python manage.py collectstatic --noinput  
3. gunicorn portfolio.wsgi:application --bind ${APP_HOST}:${APP_PORT}

This means:
- The database must be reachable at startup
- Migrations run automatically
- Static files are collected at runtime
- Startup time includes migration and static collection steps

## RUNTIME CONFIGURATION (ENVIRONMENT VARIABLES)

The container does not read a .env file internally.  
All values must be injected at runtime.

Required environment variables:

DJANGO_DEBUG=0  
DJANGO_SECRET_KEY=CHANGE_ME  
DJANGO_ALLOWED_HOSTS=example.com,www.example.com  

POSTGRES_HOST=postgres  
POSTGRES_PORT=5432  
POSTGRES_DB=portfolio  
POSTGRES_USER=portfolio  
POSTGRES_PASSWORD=CHANGE_ME  

APP_HOST=0.0.0.0  
APP_PORT=8000  

## ENVIRONMENT VARIABLE NOTES

- DJANGO_SECRET_KEY must be kept secret
- DJANGO_DEBUG must be set to 0 in production
- DJANGO_ALLOWED_HOSTS must include all public domains
- Database variables must point to a reachable PostgreSQL service

## DATABASE

PostgreSQL is not included in the image.  
The database lifecycle is managed externally.

The database must exist and be reachable when the container starts.

## MIGRATIONS

Migrations are executed automatically at container startup.

Important notes:
- Migrations must not run concurrently
- Running multiple replicas may cause migration conflicts
- Best suited for single-replica deployments unless migrations are externally coordinated

## STATIC FILES

Static files are collected at runtime using collectstatic.

The container must have write access to the static files directory.

## MEDIA UPLOADS (WAGTAIL)

If the application allows media uploads, persistent storage is required.

Options:
- Mount a persistent volume at /app/media
- Use an external object store (S3 / MinIO / compatible)

Without persistent storage:
- Uploads will be lost on container restart
- Multiple replicas will not share media

## SCALING AND REPLICAS

Recommended:
- Run with a single replica

When running multiple replicas:
- Database migrations may conflict
- Static file writes may race
- Media storage must be shared or external
- Database must support concurrent connections

## KUBERNETES NOTES

- Configuration should be provided via Kubernetes Secrets and ConfigMaps
- Ingress and TLS termination are handled externally
- This image assumes runtime migration execution

## SUMMARY

- Django + Wagtail container image
- Migrations and static collection run at startup
- No secrets baked into the image
- Runtime-configured via environment variables
- Database and storage managed externally
- Best suited for single-replica deployments
