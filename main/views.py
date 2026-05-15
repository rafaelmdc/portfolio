from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
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
                pub_groups.append({"label": label_map[key], "pubs": group})
    return {
        "educations":  Education.objects.all(),
        "experiences": Experience.objects.prefetch_related("bullets").all(),
        "pub_groups":  pub_groups,
    }


def resume_pdf(request):
    import mimetypes
    from main.cv_pdf import render_cv_pdf

    ctx = _resume_context()
    ctx["name"]      = "Rafael Correia"
    ctx["title"]     = "Software Developer & Researcher"
    ctx["email"]     = "rafaelmdcorreia@gmail.com"
    ctx["github"]    = "github.com/rafaelmdc"
    ctx["linkedin"]  = "linkedin.com/in/rafael-alexandre-correia-2b8a33213"
    ctx["skills"]    = Skill.objects.filter(active=True).order_by("order", "id")
    ctx["grants"]    = Grant.objects.all()
    ctx["awards"]    = Award.objects.all()
    ctx["languages"] = Language.objects.all()

    img_bytes, img_mime = None, None
    row = (SiteAsset.objects.filter(key="home_profile", active=True)
           .order_by("-updated_at", "-id").first())
    if row:
        try:
            img_mime = mimetypes.guess_type(row.image.name)[0] or "image/jpeg"
            with row.image.open("rb") as fh:
                img_bytes = fh.read()
        except Exception:
            pass

    try:
        pdf = render_cv_pdf(ctx, profile_image_bytes=img_bytes, profile_image_mime=img_mime)
    except RuntimeError as exc:
        return HttpResponse(str(exc), status=500, content_type="text/plain")

    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="cv_rafael_correia.pdf"'
    return response
