from django.shortcuts import render, get_object_or_404
from .models import Education, Experience, Skill
from .models import PortfolioCategory, PortfolioItem
from .models import SiteCopy, SiteAsset
import markdown as md, bleach

# ---------- COPY / ASSET HELPERS ----------
def _copy_dict():
    copy = {}
    for key, _label in SiteCopy.COPY_KEYS:
        row = (SiteCopy.objects
               .filter(key=key, active=True)
               .order_by("-updated_at", "-id")
               .first())
        copy[key] = row.text if row else ""
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

def portfolio(request):
    categories = PortfolioCategory.objects.filter(active=True).order_by("order", "name")
    items = (PortfolioItem.objects
             .prefetch_related("categories")
             .filter(active=True, categories__active=True)
             .distinct()
             .order_by("order", "id"))
    return render(request, "portfolio.html", {
        "page": {"title": "Portfolio", "lead": "Selected projects and research."},
        "categories": categories,
        "items": items,
    })

# ---------- SANITIZATION / RENDER ----------
ALLOWED_TAGS = bleach.sanitizer.ALLOWED_TAGS | {
    "p","img","h1","h2","h3","h4","h5","h6","pre","code",
    "table","thead","tbody","tr","th","td","hr","br",
    "blockquote","ul","ol","li","span","div"
}
ALLOWED_ATTRS = {
    **bleach.sanitizer.ALLOWED_ATTRIBUTES,
    "img": ["src","alt","title"],
    "a": ["href","title","rel","target"],
    "*": ["class","id"],
}

TRUST_ADMIN_HTML = False
def render_html_safe(html: str) -> str:
    if TRUST_ADMIN_HTML:
        return html or ""
    return bleach.clean(html or "", tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRS, strip=True)

def portfolio_detail(request, slug):
    item = get_object_or_404(
        PortfolioItem.objects.prefetch_related("categories"),
        slug=slug, active=True
    )

    # CKEditor field: use it directly
    body_html = (item.body_html or "").strip()
    if not body_html:
        body_html = "<p class='text-muted'>No content yet.</p>"


    # Safe hero url
    hero_url = None
    for field in ("hero", "image"):
        f = getattr(item, field, None)
        if f:
            try:
                hero_url = f.url
                break
            except Exception:
                pass

    prev_item = (PortfolioItem.objects
                 .filter(active=True, order__lt=item.order)
                 .order_by("-order")
                 .first())
    next_item = (PortfolioItem.objects
                 .filter(active=True, order__gt=item.order)
                 .order_by("order")
                 .first())

    return render(request, "portfolio_detail.html", {
        "item": item,
        "body_html": body_html,
        "hero_url": hero_url,
        "prev_item": prev_item,
        "next_item": next_item,
    })

def contact(request):
    return render(request, "contact.html")

def starter(request):
    return render(request, "starter.html")


def portfolio_view(request):
    categories = PortfolioCategory.objects.filter(active=True).order_by("order","name")
    items = (PortfolioItem.objects
             .prefetch_related("categories")
             .filter(active=True, categories__active=True)
             .distinct()
             .order_by("order","id"))
    return render(request, "portfolio.html", {"categories": categories, "items": items})
