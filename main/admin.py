from django.contrib import admin
from .models import (
    Education, Experience, ExperienceBullet,
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