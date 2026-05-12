FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System deps (Pillow + WeasyPrint)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libjpeg62-turbo-dev \
    zlib1g-dev \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libcairo2 \
    libffi-dev \
    shared-mime-info \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

# Default internal bind (compose/.env overrides these)
ENV APP_HOST=0.0.0.0 \
    APP_PORT=8000 \
    DJANGO_SETTINGS_MODULE=portfolio.settings.prod

CMD ["sh", "-lc", "set -e; python manage.py migrate; python manage.py collectstatic --noinput; exec gunicorn portfolio.wsgi:application --bind ${APP_HOST}:${APP_PORT}"]
