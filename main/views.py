from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template.loader import render_to_string
from .models import Education, Experience, Skill, Publication, PUB_TYPE_CHOICES, PUB_TYPE_ORDER
from .models import Grant, Award, Language
from .models import SiteCopy, SiteAsset

# ---------- COPY / ASSET HELPERS ----------
def _copy_dict():
    rows = SiteCopy.objects.filter(active=True).order_by("-updated_at", "-id")
    seen = set()
    copy = {k: "" for k, _ in SiteCopy.COPY_KEYS}
    for row in rows:
        if row.key not in seen:
            copy[row.key] = row.text
            seen.add(row.key)
    return copy

def _asset_url(key):
    row = (SiteAsset.objects
           .filter(key=key, active=True)
           .order_by("-updated_at", "-id")
           .first())
    return row.image.url if row else ""

# ---------- PAGES ----------
def about(request):
    context = {
        "skills": Skill.objects.filter(active=True).order_by("order", "id"),
        "copy": _copy_dict(),
        "assets": {
            "about_profile": _asset_url("about_profile"),
        },
    }
    return render(request, "about.html", context)

def index(request):
    context = {
        "assets": {
            "home_profile": _asset_url("home_profile"),
        },
    }
    return render(request, "index.html", context)

def resume(request):
    return render(request, "resume.html", _resume_context())

def contact(request):
    return render(request, "contact.html")


def _resume_context():
    pubs = list(Publication.objects.all())
    pub_groups = []
    if pubs:
        label_map = dict(PUB_TYPE_CHOICES)
        for key in PUB_TYPE_ORDER:
            group = [p for p in pubs if p.pub_type == key]
            if group:
                pub_groups.append({"label": label_map[key], "items": group})
    return {
        "educations":  Education.objects.all(),
        "experiences": Experience.objects.prefetch_related("bullets").all(),
        "pub_groups":  pub_groups,
    }


def _profile_image_data_uri():
    """Return a base64 data URI for the home profile image, or empty string."""
    import base64, mimetypes
    row = (SiteAsset.objects
           .filter(key="home_profile", active=True)
           .order_by("-updated_at", "-id")
           .first())
    if not row:
        return ""
    try:
        mime = mimetypes.guess_type(row.image.name)[0] or "image/jpeg"
        with row.image.open("rb") as f:
            data = base64.b64encode(f.read()).decode()
        return f"data:{mime};base64,{data}"
    except Exception:
        return ""


def resume_pdf(request):
    try:
        from weasyprint import HTML
    except ImportError:
        return HttpResponse("WeasyPrint is not installed.", status=503, content_type="text/plain")

    ctx = _resume_context()
    ctx["profile_image"] = _profile_image_data_uri()
    ctx["skills"]     = Skill.objects.filter(active=True).order_by("order", "id")
    ctx["grants"]     = Grant.objects.all()
    ctx["awards"]     = Award.objects.all()
    ctx["languages"]  = Language.objects.all()

    html = render_to_string("resume_pdf.html", ctx, request=request)
    pdf  = HTML(string=html).write_pdf()
    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="cv_rafael_correia.pdf"'
    return response
