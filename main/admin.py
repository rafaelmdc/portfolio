from django.contrib import admin

# Register your models here.
from .models import Education, Experience, ExperienceBullet, SiteCopy, Skill

@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ("title", "institution", "start_year", "end_year", "order")
    list_editable = ("order",)
    search_fields = ("title", "institution", "blurb")

class ExperienceBulletInline(admin.TabularInline):  # or StackedInline if you prefer
    model = ExperienceBullet
    extra = 2
    min_num = 0
    fields = ("text", "order")

@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ("role", "company", "start_year", "end_year", "order")
    list_editable = ("order",)
    search_fields = ("role", "company", "blurb")
    inlines = [ExperienceBulletInline]

@admin.register(SiteCopy)
class SiteCopyAdmin(admin.ModelAdmin):
    list_display = ("key", "short_text", "active", "updated_at")
    list_filter = ("key", "active")
    list_editable = ("active",)
    search_fields = ("text",)
    ordering = ("key", "-active", "-updated_at")

    def short_text(self, obj):
        return (obj.text[:80] + "…") if len(obj.text) > 80 else obj.text
    short_text.short_description = "Text"

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("name", "order", "active", "updated_at")
    list_editable = ("order", "active")
    search_fields = ("name", "description")
    list_filter = ("active",)
    ordering = ("order", "name")
