from django.contrib import admin

# Register your models here.
from .models import Education, Experience, ExperienceBullet

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