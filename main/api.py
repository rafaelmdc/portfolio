"""
Custom headless endpoint for the single-page landing site.

GET /api/v2/site/ returns one bundle the Next.js landing page needs: editable
copy, profile images (rendition URLs), the CV snippets (skills, education,
experience, publications, grants, awards, languages), live GitHub stats and a
`has_research` flag that drives the adaptive research section.

Blog and portfolio content come from the Wagtail pages API (/api/v2/pages/).
"""
from django.conf import settings
from django.core.cache import cache
from rest_framework.response import Response
from rest_framework.views import APIView

import requests

from .models import (
    SiteContent, Skill, Education, Experience, Publication,
    Grant, Award, Language, PUB_TYPE_CHOICES, PUB_TYPE_ORDER,
)

GITHUB_CACHE_TTL = 3600  # 1 hour


def _img(image, spec_full="width-1200", spec_thumb="fill-600x400"):
    if not image:
        return None
    full = image.get_rendition(spec_full)
    thumb = image.get_rendition(spec_thumb)
    return {
        "url": full.url, "width": full.width, "height": full.height,
        "thumb": thumb.url, "alt": image.title,
    }


def github_stats(username, ttl=GITHUB_CACHE_TTL):
    if not username:
        return None
    key = f"github_stats:{username}"
    cached = cache.get(key)
    if cached is not None:
        return cached or None
    try:
        user = requests.get(
            f"https://api.github.com/users/{username}", timeout=6
        ).json()
        repos = requests.get(
            f"https://api.github.com/users/{username}/repos?per_page=100&type=owner",
            timeout=8,
        ).json()
        if not isinstance(repos, list):
            repos = []
        langs = {}
        for r in repos:
            lang = r.get("language")
            if lang:
                langs[lang] = langs.get(lang, 0) + 1
        # Lifetime public commits authored by the user (search API, cached).
        total_commits = None
        try:
            sr = requests.get(
                "https://api.github.com/search/commits",
                params={"q": f"author:{username}", "per_page": 1},
                headers={"Accept": "application/vnd.github+json"},
                timeout=8,
            ).json()
            if isinstance(sr, dict) and "total_count" in sr:
                total_commits = sr["total_count"]
        except Exception:
            pass

        data = {
            "username": username,
            "public_repos": user.get("public_repos"),
            "followers": user.get("followers"),
            "total_stars": sum(r.get("stargazers_count", 0) for r in repos),
            "top_language": max(langs, key=langs.get) if langs else None,
            "total_commits": total_commits,
        }
    except Exception:
        data = None
    # Cache success for the full TTL, failures briefly so we retry soon.
    cache.set(key, data or {}, ttl if data else 120)
    return data


def _education(e):
    return {
        "title": e.title, "institution": e.institution, "location": e.location,
        "start_year": e.start_year, "end_year": e.end_year, "blurb": e.blurb,
    }


def _experience(x):
    return {
        "role": x.role, "company": x.company, "location": x.location,
        "start_year": x.start_year, "end_year": x.end_year, "blurb": x.blurb,
        "bullets": [b.text for b in x.bullets.all()],
    }


def _publication(p):
    return {
        "title": p.title, "authors": p.authors, "authors_display": p.authors_display,
        "venue": p.venue, "year": p.year, "pub_type": p.pub_type,
        "doi": p.doi, "url": p.url, "link": p.link,
        "citation_count": p.citation_count, "featured": p.featured,
    }


def _home_sections():
    """Serialise the HomePage section StreamField (incl. image renditions)."""
    from cms.models import HomePage

    home = HomePage.objects.first()
    if not home or not home.sections:
        return []
    return home.sections.stream_block.get_api_representation(home.sections, {})


def _live_projects_count():
    """Number of published portfolio projects (for the 'projects shipped' stat)."""
    from cms.models import PortfolioProjectPage

    return PortfolioProjectPage.objects.live().public().count()


def _uses(sc):
    """Serialise the /uses StreamField into clean category/item objects."""
    if not sc or not sc.uses:
        return []
    out = []
    for block in sc.uses:
        if block.block_type != "category":
            continue
        v = block.value
        out.append({
            "heading": str(v.get("heading", "")),
            "items": [
                {
                    "name": str(it.get("name", "")),
                    "detail": str(it.get("detail", "")),
                    "url": str(it.get("url", "")),
                }
                for it in v.get("items", [])
            ],
        })
    return out


class SiteBundleView(APIView):
    def get(self, request):
        sc = SiteContent.objects.first()

        copy = {
            k: (getattr(sc, k, "") or "") if sc else ""
            for k in [
                "about_title", "about_lead", "about_intro_headline",
                "about_intro_body", "about_quote", "skills_title", "skills_lead",
                "hero_eyebrow", "hero_headline", "hero_highlight",
                "hero_cta_primary", "hero_cta_secondary",
                "contact_headline", "contact_note", "about_focus",
            ]
        }

        pubs = list(Publication.objects.all())
        label_map = dict(PUB_TYPE_CHOICES)
        groups = [
            {"label": label_map[key], "items": [_publication(p) for p in pubs if p.pub_type == key]}
            for key in PUB_TYPE_ORDER
            if any(p.pub_type == key for p in pubs)
        ]

        return Response({
            "copy": copy,
            "images": {
                "about_profile": _img(sc.about_profile) if sc else None,
                "home_profile": _img(sc.home_profile) if sc else None,
            },
            "skills": [
                {"name": s.name, "description": s.description, "icon": s.icon}
                for s in Skill.objects.filter(active=True).order_by("order", "id")
            ],
            "education": [_education(e) for e in Education.objects.all()],
            "experience": [
                _experience(x) for x in Experience.objects.prefetch_related("bullets").all()
            ],
            "publications": {"groups": groups, "flat": [_publication(p) for p in pubs]},
            "grants": [
                {"title": g.title, "funder": g.funder, "role": g.role, "amount": g.amount,
                 "start_year": g.start_year, "end_year": g.end_year,
                 "description": g.description, "url": g.url}
                for g in Grant.objects.all()
            ],
            "awards": [
                {"title": a.title, "issuer": a.issuer, "year": a.year,
                 "description": a.description, "url": a.url}
                for a in Award.objects.all()
            ],
            "languages": [
                {"name": l.name, "level": l.level, "level_display": l.get_level_display()}
                for l in Language.objects.all()
            ],
            "github": github_stats(sc.github_username if sc else ""),
            "orcid_id": getattr(settings, "ORCID_ID", ""),
            "has_research": bool(pubs),
            "sections": _home_sections(),
            "contact": {
                "email": (sc.email if sc else "") or "",
                "linkedin_url": (sc.linkedin_url if sc else "") or "",
                "github_username": (sc.github_username if sc else "") or "",
                "full_name": (sc.full_name if sc else "") or "",
                "role_title": (sc.role_title if sc else "") or "",
                "show_email": bool(sc.contact_show_email) if sc else True,
                "show_github": bool(sc.contact_show_github) if sc else True,
                "show_linkedin": bool(sc.contact_show_linkedin) if sc else True,
                "show_blog": bool(sc.contact_show_blog) if sc else True,
            },
            "stats": {
                k: bool(getattr(sc, k)) if sc else False
                for k in [
                    "stat_focus", "stat_repos", "stat_stars", "stat_language",
                    "stat_followers", "stat_commits", "stat_publications", "stat_honors",
                    "stat_building", "stat_projects", "stat_status", "stat_domain",
                ]
            },
            "about_extra": {
                "building_since": (sc.building_since if sc else None) or None,
                "projects_count": _live_projects_count(),
                "current_status": (sc.current_status if sc else "") or "",
                "primary_domain": (sc.primary_domain if sc else "") or "",
            },
            "uses": {
                "intro": (sc.uses_intro if sc else "") or "",
                "categories": _uses(sc),
            },
            "cv": {
                "enabled": bool(sc.cv_enabled) if sc else False,
                # Slashless so the frontend proxy doesn't hit an APPEND_SLASH
                # loop; regenerates-if-stale then redirects to the inline PDF.
                "url": "/resume/pdf" if (sc and sc.cv_enabled) else "",
            },
        })
