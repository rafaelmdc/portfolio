from django.http import HttpResponse
from django.shortcuts import redirect

from .models import SiteContent


def _site_content():
    return SiteContent.objects.first()


def root(request):
    """Headless backend — there is no public page here; send visitors to the CMS."""
    return redirect("/cms/")


def resume_pdf(request):
    """Open the cached, auto-generated CV PDF (regenerated only when stale)."""
    from main.cv import get_cv_document

    doc = get_cv_document(_site_content())
    if not doc:
        return HttpResponse("CV is unavailable.", status=404, content_type="text/plain")
    return redirect(doc.url)
