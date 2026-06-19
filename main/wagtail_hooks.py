# main/wagtail_hooks.py
"""
Registers the CV / résumé models as Wagtail snippets so all content is editable
from the single Wagtail admin (/cms). Schema-neutral: these are the existing
Django models, just surfaced in Wagtail with list views mirroring the old
django-admin config.
"""
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet, SnippetViewSetGroup

from .models import (
    Education, Experience, Publication,
    Grant, Award, Language, Skill,
)


class ExperienceViewSet(SnippetViewSet):
    model = Experience
    icon = "user"
    menu_label = "Experience"
    list_display = ("role", "company", "start_year", "end_year", "order")
    search_fields = ("role", "company", "blurb")
    ordering = ("order", "-start_year")


class EducationViewSet(SnippetViewSet):
    model = Education
    icon = "date"
    menu_label = "Education"
    list_display = ("title", "institution", "start_year", "end_year", "order")
    search_fields = ("title", "institution", "blurb")
    ordering = ("order", "-start_year")


class PublicationViewSet(SnippetViewSet):
    model = Publication
    icon = "doc-full"
    menu_label = "Publications"
    list_display = ("year", "title", "pub_type", "venue", "citation_count", "featured", "order")
    list_filter = ("pub_type", "featured")
    search_fields = ("title", "authors", "venue", "doi")
    ordering = ("-year", "order")


class SkillViewSet(SnippetViewSet):
    model = Skill
    icon = "tag"
    menu_label = "Skills"
    list_display = ("name", "order", "active")
    list_filter = ("active",)
    search_fields = ("name", "description")
    ordering = ("order", "name")


class GrantViewSet(SnippetViewSet):
    model = Grant
    icon = "pick"
    menu_label = "Grants"
    list_display = ("title", "funder", "role", "amount", "start_year", "end_year", "order")
    search_fields = ("title", "funder", "description")
    ordering = ("-start_year", "order")


class AwardViewSet(SnippetViewSet):
    model = Award
    icon = "success"
    menu_label = "Awards"
    list_display = ("title", "issuer", "year", "order")
    search_fields = ("title", "issuer", "description")
    ordering = ("-year", "order")


class LanguageViewSet(SnippetViewSet):
    model = Language
    icon = "globe"
    menu_label = "Languages"
    list_display = ("name", "level", "order")
    ordering = ("order", "id")


class CVViewSetGroup(SnippetViewSetGroup):
    menu_label = "CV"
    menu_icon = "clipboard-list"
    menu_order = 200
    items = (
        ExperienceViewSet,
        EducationViewSet,
        PublicationViewSet,
        SkillViewSet,
        GrantViewSet,
        AwardViewSet,
        LanguageViewSet,
    )


register_snippet(CVViewSetGroup)
