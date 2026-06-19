from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent.parent

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'django.contrib.postgres',
    "main",
    # Wagtail
    "wagtail.contrib.forms",
    "wagtail.contrib.redirects",
    "wagtail.contrib.settings",
    "wagtail.contrib.table_block",
    "wagtail.embeds",
    "wagtail.sites",
    "wagtail.users",
    "wagtail.snippets",
    "wagtail.documents",
    "wagtail.images",
    "wagtail.search",
    "wagtail.admin",
    "wagtail",
    "wagtail.api.v2",
    "wagtail_headless_preview",
    "rest_framework",
    "modelcluster",
    "taggit",
    "cms",
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "wagtail.contrib.redirects.middleware.RedirectMiddleware",
]

ROOT_URLCONF = 'portfolio.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'portfolio.wsgi.application'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

WAGTAIL_SITE_NAME = "Portfolio"

# Allow the headless frontend to fetch the full blog/portfolio list in one call.
WAGTAILAPI_LIMIT_MAX = 100
WAGTAILADMIN_BASE_URL = os.environ.get("WAGTAIL_BASE_URL", "http://localhost:3000")

# Open PDFs (e.g. the generated CV) inline in the browser instead of downloading.
WAGTAILDOCS_INLINE_CONTENT_TYPES = ["application/pdf"]

# Public Next.js frontend base URL. Headless page serve/preview redirect here,
# and the CMS "Preview" opens <FRONTEND_BASE_URL>/preview?content_type=&token=.
FRONTEND_BASE_URL = os.environ.get("FRONTEND_BASE_URL", "http://localhost:8000").rstrip("/")
WAGTAIL_HEADLESS_PREVIEW = {
    "CLIENT_URLS": {"default": FRONTEND_BASE_URL + "/preview"},
    "SERVE_BASE_URL": FRONTEND_BASE_URL,
    "REDIRECT_ON_PREVIEW": True,
    "ENFORCE_TRAILING_SLASH": False,
}

# Optional: ORCID public profile ID (e.g. "0000-0001-2345-6789")
ORCID_ID             = os.environ.get("ORCID_ID", "")
# Your name as it appears in ORCID author lists — bolded in the PDF CV
ORCID_HIGHLIGHT_NAME = os.environ.get("ORCID_HIGHLIGHT_NAME", "")


def env_list(name: str, default: str = "") -> list[str]:
    return [x.strip() for x in os.getenv(name, default).split(",") if x.strip()]
