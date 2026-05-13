from django.contrib import admin
from .models import (
    Education, Experience, ExperienceBullet,
    Publication, Grant, Award, Language,
    Skill, SiteCopy, SiteAsset,
)


# ---------------- CV ----------------
@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ("title", "institution", "start_year", "end_year", "order")
    list_editable = ("order",)
    search_fields = ("title", "institution", "blurb")
    ordering = ("order", "-start_year")


class ExperienceBulletInline(admin.TabularInline):
    model = ExperienceBullet
    extra = 2
    fields = ("text", "order")
    ordering = ("order", "id")


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ("role", "company", "start_year", "end_year", "order")
    list_editable = ("order",)
    search_fields = ("role", "company", "blurb")
    inlines = [ExperienceBulletInline]
    ordering = ("order", "-start_year")


@admin.register(Publication)
class PublicationAdmin(admin.ModelAdmin):
    list_display  = ("year", "short_title", "pub_type", "venue", "citation_count", "featured", "order")
    list_editable = ("order", "featured")
    list_filter   = ("pub_type", "featured")
    search_fields = ("title", "authors", "venue", "doi")
    ordering      = ("-year", "order")
    fieldsets = (
        (None, {"fields": ("title", "authors", "highlight_name", "venue", "year", "pub_type")}),
        ("Links", {"fields": ("doi", "url")}),
        ("Details", {"fields": ("abstract", "citation_count", "featured", "order")}),
        ("ORCID sync", {"fields": ("orcid_put_code",), "classes": ("collapse",)}),
    )

    def short_title(self, obj):
        return obj.title[:60] + "…" if len(obj.title) > 60 else obj.title
    short_title.short_description = "Title"


@admin.register(Grant)
class GrantAdmin(admin.ModelAdmin):
    list_display  = ("title", "funder", "role", "amount", "start_year", "end_year", "order")
    list_editable = ("order",)
    search_fields = ("title", "funder", "description")
    ordering      = ("-start_year", "order")
    fieldsets = (
        (None,        {"fields": ("title", "funder", "role", "amount", "start_year", "end_year")}),
        ("Details",   {"fields": ("description", "url")}),
        ("ORCID sync",{"fields": ("orcid_put_code",), "classes": ("collapse",)}),
    )


@admin.register(Award)
class AwardAdmin(admin.ModelAdmin):
    list_display  = ("title", "issuer", "year", "order")
    list_editable = ("order",)
    search_fields = ("title", "issuer", "description")
    ordering      = ("-year", "order")


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display  = ("name", "level", "order")
    list_editable = ("level", "order")
    ordering      = ("order", "id")


# ------------- Site Copy / Assets -------------
@admin.register(SiteCopy)
class SiteCopyAdmin(admin.ModelAdmin):
    list_display = ("key", "active", "updated_at")
    list_filter = ("key", "active")
    list_editable = ("active",)
    search_fields = ("text",)
    ordering = ("key", "-active", "-updated_at")


@admin.register(SiteAsset)
class SiteAssetAdmin(admin.ModelAdmin):
    list_display = ("key", "preview", "active", "updated_at")
    list_filter = ("key", "active")
    list_editable = ("active",)
    ordering = ("key", "-active", "-updated_at")

    def preview(self, obj):
        try:
            return f"{obj.image.width}×{obj.image.height}"
        except Exception:
            return "—"
    preview.short_description = "Size"


# ---------------- Skills ----------------
@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("name", "order", "active", "updated_at")
    list_editable = ("order", "active")
    search_fields = ("name", "description")
    list_filter = ("active",)
    ordering = ("order", "name")