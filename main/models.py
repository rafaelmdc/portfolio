from django.db import models

# Create your models here.

class Education(models.Model):
    title = models.CharField(max_length=200)
    institution = models.CharField(max_length=200)
    location = models.CharField(max_length=200, blank=True)
    start_year = models.PositiveIntegerField()
    end_year = models.PositiveIntegerField(null=True, blank=True)  # null => Present
    blurb = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "-start_year"]

    def __str__(self):
        return f"{self.title} @ {self.institution}"


class Experience(models.Model):
    role = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    location = models.CharField(max_length=200, blank=True)
    start_year = models.PositiveIntegerField()
    end_year = models.PositiveIntegerField(null=True, blank=True)  # null => Present
    blurb = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "-start_year"]

    def __str__(self):
        return f"{self.role} @ {self.company}"


class ExperienceBullet(models.Model):
    experience = models.ForeignKey(
        Experience, on_delete=models.CASCADE, related_name="bullets"
    )
    text = models.CharField(max_length=300)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.text

# app: portfolio/models.py
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator

class Timestamped(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True

class SiteCopy(Timestamped):
    """
    Small key–value store for page copy.
    Only one 'active' row per key should be live.
    """
    COPY_KEYS = [
        ("about_title", "About: Section Title"),
        ("about_lead", "About: Lead Paragraph"),
        ("about_intro_headline", "About: Intro Headline"),
        ("about_intro_body", "About: Intro Body"),
        ("skills_title", "Skills: Section Title"),
        ("skills_lead", "Skills: Lead Paragraph"),
        ("about_quote", "About: Quote"),
    ]

    key = models.CharField(max_length=64, choices=COPY_KEYS, db_index=True)
    text = models.TextField()
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Site Copy"
        indexes = [models.Index(fields=["key", "active"])]

    def clean(self):
        if self.active:
            qs = SiteCopy.objects.filter(key=self.key, active=True)
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            if qs.exists():
                raise ValidationError(f"Only one active entry is allowed for key='{self.key}'.")

    def __str__(self):
        return f"{self.get_key_display()} ({'active' if self.active else 'inactive'})"


class Skill(Timestamped):
    name = models.CharField(max_length=80)
    description = models.CharField(max_length=240, blank=True)
    order = models.PositiveIntegerField(default=0, db_index=True)
    active = models.BooleanField(default=True)
    icon = models.CharField(
        max_length=64, blank=True,
        help_text="Optional Bootstrap Icon class (e.g., 'bi-code-slash')."
    )

    class Meta:
        ordering = ("order", "id")

    def __str__(self):
        return self.name
