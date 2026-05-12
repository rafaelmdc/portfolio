from .base import *  # noqa: F401, F403
import os

DEBUG = True

SECRET_KEY = "dev-only-insecure-secret-key-do-not-use-in-production"

ALLOWED_HOSTS = ["*"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB", "portfolio"),
        "USER": os.environ.get("POSTGRES_USER", "portfolio"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "portfolio"),
        "HOST": os.environ.get("POSTGRES_HOST", "localhost"),
        "PORT": os.environ.get("POSTGRES_PORT", "5432"),
    }
}

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}
