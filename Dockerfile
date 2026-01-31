FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System deps (Pillow etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libjpeg62-turbo-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

# Default internal bind (compose/.env overrides these)
ENV APP_HOST=0.0.0.0 \
    APP_PORT=8000

CMD ["sh", "-lc", "set -e; python manage.py migrate; python manage.py collectstatic --noinput; exec gunicorn portfolio.wsgi:application --bind ${APP_HOST}:${APP_PORT}"]
