from django.contrib import admin
from django.urls import path, include

from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls
from wagtail import urls as wagtail_urls

from django.conf import settings
from django.views.static import serve

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("main.urls")),

    path("cms/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),

    # Serve MEDIA in production (personal site)
    path("media/<path:path>", serve, {"document_root": settings.MEDIA_ROOT}),

    # Wagtail catch-all LAST
    path("", include(wagtail_urls)),
]
