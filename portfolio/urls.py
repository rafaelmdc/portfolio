from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.contrib.sitemaps.views import sitemap

from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls
from wagtail import urls as wagtail_urls
from wagtail.contrib.sitemaps import Sitemap as WagtailSitemap

from django.conf import settings
from main.sitemaps import StaticViewSitemap

sitemaps = {
    "static": StaticViewSitemap,
    "wagtail": WagtailSitemap,
}

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("main.urls")),

    path("cms/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),

    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
    path("robots.txt", TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),

    # Wagtail catch-all LAST
    path("", include(wagtail_urls)),
]

if settings.DEBUG:
    from django.views.static import serve
    urlpatterns += [
        path("media/<path:path>", serve, {"document_root": settings.MEDIA_ROOT}),
    ]
