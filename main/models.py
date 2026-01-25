# main/models.py
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field

import os, uuid


# ---------- helpers ----------
def site_upload_to(_instance, filename):
    ext = os.path.splitext(filename)[1].lower()
    return f"site/{uuid.uuid4().hex}{ext}"


def upload_portfolio_img(_instance, filename):
    ext = os.path.splitext(filename)[1].lower()
    return f"portfolio/{uuid.uuid4().hex}{ext}"


# ---------- base ----------
class Timestamped(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# ---------- CV sections ----------
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


# ---------- site copy / assets ----------
class SiteCopy(Timestamped):
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
                raise ValidationError(
                    f"Only one active entry is allowed for key='{self.key}'."
                )

    def __str__(self):
        return f"{self.get_key_display()} ({'active' if self.active else 'inactive'})"


class SiteAsset(Timestamped):
    """
    Single active asset per key (like SiteCopy but for images/files).
    """

    ASSET_KEYS = [
        ("about_profile", "About: Profile Image"),
        ("home_profile", "Home: Profile Image"),
        # add more later (e.g., "home_hero", "resume_pdf", etc.)
    ]

    key = models.CharField(max_length=64, choices=ASSET_KEYS, db_index=True)
    image = models.ImageField(upload_to=site_upload_to)
    alt_text = models.CharField(max_length=160, blank=True)
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Site Asset"
        verbose_name_plural = "Site Assets"
        indexes = [models.Index(fields=["key", "active"])]

    def clean(self):
        if self.active:
            qs = SiteAsset.objects.filter(key=self.key, active=True)
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            if qs.exists():
                raise ValidationError(
                    f"Only one active asset is allowed for key='{self.key}'."
                )

    def __str__(self):
        return f"{self.get_key_display()} ({'active' if self.active else 'inactive'})"


class Skill(Timestamped):
    name = models.CharField(max_length=80)
    description = models.CharField(max_length=240, blank=True)
    order = models.PositiveIntegerField(default=0, db_index=True)
    active = models.BooleanField(default=True)
    icon = models.CharField(
        max_length=64,
        blank=True,
        help_text="Optional Bootstrap Icon class (e.g., 'bi-code-slash').",
    )

    class Meta:
        ordering = ("order", "id")

    def __str__(self):
        return self.name


# ---------- portfolio ----------
class PortfolioCategory(Timestamped):
    name = models.CharField(max_length=60, unique=True)
    slug = models.SlugField(max_length=60, unique=True, blank=True)
    order = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ("order", "name")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class PortfolioItem(Timestamped):
    title = models.CharField(max_length=140)
    slug = models.SlugField(max_length=160, unique=True, blank=True)
    subtitle = models.CharField(max_length=160, blank=True)

    # many categories = tags
    categories = models.ManyToManyField(
        PortfolioCategory, related_name="items", blank=True
    )

    # images
    image = models.ImageField(upload_to=upload_portfolio_img)  # grid thumbnail
    hero = models.ImageField(
        upload_to=upload_portfolio_img, blank=True, null=True
    )  # detail header
    lightbox_image = models.ImageField(
        upload_to=upload_portfolio_img, blank=True, null=True
    )

    external_url = models.URLField(blank=True)

    # detail content (CKEditor stores raw HTML + allows uploads)
    body_html = CKEditor5Field("Body", config_name="default")

    order = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ("order", "id")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:160] or uuid.uuid4().hex[:12]
        super().save(*args, **kwargs)

    def lightbox_url(self):
        return (self.lightbox_image or self.image).url

    def __str__(self):
        return self.title

def portfolio_upload_to(instance, filename):
    """
    Backwards-compat function required by migration 0005.
    Keep this importable forever, or until you squash migrations.
    """
    # If you have a new function elsewhere, delegate to it:
    # from .utils import new_portfolio_upload_to
    # return new_portfolio_upload_to(instance, filename)

    # Minimal safe fallback:
    name, ext = os.path.splitext(filename)
    # Try using a slug if your model has one; otherwise bucket by pk.
    slug = getattr(instance, "slug", None) or f"item-{getattr(instance, 'pk', 'new')}"
    return f"portfolio/{slug}/{uuid.uuid4().hex}{ext.lower()}"