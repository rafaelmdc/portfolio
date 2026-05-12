from django.shortcuts import render, get_object_or_404
from .models import Education, Experience, Skill
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
    ctx = {
        "educations": Education.objects.all(),
        "experiences": Experience.objects.prefetch_related("bullets").all(),
    }
    return render(request, "resume.html", ctx)

def contact(request):
    return render(request, "contact.html")
