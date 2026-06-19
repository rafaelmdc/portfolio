"""
CV PDF as a cached Wagtail Document.

The PDF is rendered from the live CMS data (experience, education, skills,
publications, …) via XeLaTeX and stored in a single Wagtail Document. The
Document is the cache: it has a stable URL, opens inline, and is only
regenerated when missing or older than the configured refresh window
(daily / weekly) — never per request.
"""
import mimetypes
from datetime import timedelta

from django.core.files.base import ContentFile
from django.utils import timezone

from wagtail.documents import get_document_model

from .models import (
    Education, Experience, Skill, Publication, Grant, Award, Language,
    SiteContent, PUB_TYPE_CHOICES, PUB_TYPE_ORDER,
)

_REFRESH = {"daily": timedelta(days=1), "weekly": timedelta(weeks=1)}
_CV_FILENAME = "cv_rafael_correia.pdf"


def _resume_context(sc):
    pubs = list(Publication.objects.all())
    pub_groups = []
    if pubs:
        label_map = dict(PUB_TYPE_CHOICES)
        for key in PUB_TYPE_ORDER:
            group = [p for p in pubs if p.pub_type == key]
            if group:
                pub_groups.append({"label": label_map[key], "pubs": group})

    github = sc.github_username if sc else ""
    return {
        "name":        (sc.full_name if sc else "") or "Rafael Correia",
        "title":       (sc.role_title if sc else "") or "Software Developer & Researcher",
        "email":       (sc.email if sc else "") or "rafaelmdcorreia@gmail.com",
        "github":      f"github.com/{github}" if github else "",
        "linkedin":    (sc.linkedin_url if sc else "").replace("https://", "").replace("http://", ""),
        "skills":      Skill.objects.filter(active=True).order_by("order", "id"),
        "languages":   Language.objects.all(),
        "experiences": Experience.objects.prefetch_related("bullets").all(),
        "educations":  Education.objects.all(),
        "grants":      Grant.objects.all(),
        "awards":      Award.objects.all(),
        "pub_groups":  pub_groups,
    }


def _render_pdf_bytes(sc):
    from .cv_pdf import render_cv_pdf

    ctx = _resume_context(sc)
    img_bytes, img_mime = None, None
    img = sc.home_profile if sc else None
    if img:
        try:
            img_mime = mimetypes.guess_type(img.file.name)[0] or "image/jpeg"
            img.file.open("rb")
            img_bytes = img.file.read()
            img.file.close()
        except Exception:
            pass
    return render_cv_pdf(ctx, profile_image_bytes=img_bytes, profile_image_mime=img_mime)


def _is_stale(sc):
    if not sc or not sc.cv_document or not sc.cv_generated_at:
        return True
    window = _REFRESH.get(sc.cv_refresh, _REFRESH["weekly"])
    return timezone.now() - sc.cv_generated_at > window


def regenerate_cv_document(sc=None):
    """Render the CV and store it in the (singleton) Wagtail Document. Returns
    the Document, or None if rendering failed."""
    sc = sc or SiteContent.objects.first()
    if not sc:
        return None

    pdf = _render_pdf_bytes(sc)  # may raise RuntimeError if XeLaTeX is missing

    Document = get_document_model()
    content = ContentFile(pdf, name=_CV_FILENAME)
    doc = sc.cv_document
    if doc is None:
        doc = Document(title="CV — auto-generated")
        doc.file.save(_CV_FILENAME, content, save=True)
        sc.cv_document = doc
    else:
        doc.file.save(_CV_FILENAME, content, save=True)
    sc.cv_generated_at = timezone.now()
    sc.save(update_fields=["cv_document", "cv_generated_at"])
    return doc


def get_cv_document(sc=None):
    """Return the current CV Document, regenerating it first if missing/stale."""
    sc = sc or SiteContent.objects.first()
    if not sc or not sc.cv_enabled:
        return None
    if _is_stale(sc):
        try:
            return regenerate_cv_document(sc)
        except Exception:
            # Fall back to the existing (possibly stale) document if generation
            # fails — better a slightly old CV than a broken link.
            return sc.cv_document
    return sc.cv_document
