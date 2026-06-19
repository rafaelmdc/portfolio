"""
Headless API router (Wagtail REST API v2).

Exposes pages, images and documents under /api/v2/ for the Next.js frontend.
Per-page `api_fields` are declared on the page models in cms/models.py.
"""
from django.contrib.contenttypes.models import ContentType
from django.core.signing import BadSignature, SignatureExpired
from django.http import Http404
from rest_framework.response import Response

from wagtail.api.v2.router import WagtailAPIRouter
from wagtail.api.v2.views import PagesAPIViewSet
from wagtail.images.api.v2.views import ImagesAPIViewSet
from wagtail.documents.api.v2.views import DocumentsAPIViewSet


class PagePreviewAPIViewSet(PagesAPIViewSet):
    """
    Serialise an unsaved DRAFT page for the headless frontend's /preview route.

    Wagtail's "Preview" stores the edited page under a signed token (see
    wagtail_headless_preview) and redirects the browser to the frontend with
    ?content_type=<app.model>&token=<token>. This endpoint reconstructs that
    draft and serialises it exactly like the normal pages endpoint, so the
    frontend can render it with its real components.
    """

    known_query_parameters = PagesAPIViewSet.known_query_parameters.union(
        ["content_type", "token"]
    )

    def get_object(self):
        try:
            app_label, model = self.request.GET["content_type"].split(".")
            token = self.request.GET["token"]
        except (KeyError, ValueError):
            raise Http404("content_type and token are required")

        try:
            page_model = ContentType.objects.get(
                app_label=app_label, model=model
            ).model_class()
        except ContentType.DoesNotExist:
            raise Http404("unknown content_type")

        try:
            page = page_model.get_page_from_preview_token(token)
        except (BadSignature, SignatureExpired):
            raise Http404("invalid or expired preview token")
        if page is None:
            raise Http404("preview expired or not found")
        # A never-saved page has no pk; give it a sentinel so serialisation
        # (which builds meta URLs) doesn't choke.
        if page.pk is None:
            page.pk = 0
        return page

    def listing_view(self, request):
        # Serialise as a DETAIL view so the serializer resolves the specific
        # page model (not base Page) and exposes its full api_fields/`fields`.
        self.action = "detail_view"
        page = self.get_object()
        serializer = self.get_serializer(page)
        return Response(serializer.data)

    def detail_view(self, request, pk):
        return self.listing_view(request)


api_router = WagtailAPIRouter("wagtailapi")

api_router.register_endpoint("pages", PagesAPIViewSet)
api_router.register_endpoint("page_preview", PagePreviewAPIViewSet)
api_router.register_endpoint("images", ImagesAPIViewSet)
api_router.register_endpoint("documents", DocumentsAPIViewSet)
