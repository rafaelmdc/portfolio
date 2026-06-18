from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Education, Experience, Skill, Publication, PUB_TYPE_CHOICES, PUB_TYPE_ORDER
from .models import Grant, Award, Language
from .models import SiteContent

# ---------- SITE CONTENT HELPERS ----------
COPY_KEYS = [
    "about_title", "about_lead", "about_intro_headline",
    "about_intro_body", "about_quote", "skills_title", "skills_lead",
]


def _site_content():
    return SiteContent.objects.first()


def _copy_dict(sc):
    if not sc:
        return {k: "" for k in COPY_KEYS}
    return {k: (getattr(sc, k, "") or "") for k in COPY_KEYS}


def _image_url(img, spec="width-1024"):
    if not img:
        return ""
    try:
        return img.get_rendition(spec).url
    except Exception:
        try:
            return img.file.url
        except Exception:
            return ""

# ---------- PAGES ----------
def about(request):
    sc = _site_content()
    context = {
        "skills": Skill.objects.filter(active=True).order_by("order", "id"),
        "copy": _copy_dict(sc),
        "assets": {
            "about_profile": _image_url(sc.about_profile if sc else None),
        },
    }
    return render(request, "about.html", context)

def index(request):
    sc = _site_content()
    context = {
        "assets": {
            "home_profile": _image_url(sc.home_profile if sc else None),
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
    sc = _site_content()
    img = sc.home_profile if sc else None
    if img:
        try:
            img_mime = mimetypes.guess_type(img.file.name)[0] or "image/jpeg"
            img.file.open("rb")
            img_bytes = img.file.read()
            img.file.close()
        except Exception:
            pass

    try:
        pdf = render_cv_pdf(ctx, profile_image_bytes=img_bytes, profile_image_mime=img_mime)
    except RuntimeError as exc:
        return HttpResponse(str(exc), status=500, content_type="text/plain")

    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="cv_rafael_correia.pdf"'
    return response
