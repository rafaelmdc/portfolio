# main/models.py
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.text import slugify

import os, uuid
from .validators import validate_image_file

from modelcluster.models import ClusterableModel
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, InlinePanel


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
        verbose_name = "Education"
        verbose_name_plural = "Education entries"

    def __str__(self):
        return f"{self.title} @ {self.institution}"

    panels = [
        FieldPanel("title"),
        FieldPanel("institution"),
        FieldPanel("location"),
        MultiFieldPanel(
            [FieldPanel("start_year"), FieldPanel("end_year")],
            heading="Years",
        ),
        FieldPanel("blurb"),
        FieldPanel("order"),
    ]


class Experience(ClusterableModel):
    role = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    location = models.CharField(max_length=200, blank=True)
    start_year = models.PositiveIntegerField()
    end_year = models.PositiveIntegerField(null=True, blank=True)  # null => Present
    blurb = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "-start_year"]
        verbose_name = "Experience"
        verbose_name_plural = "Experience entries"

    def __str__(self):
        return f"{self.role} @ {self.company}"

    panels = [
        FieldPanel("role"),
        FieldPanel("company"),
        FieldPanel("location"),
        MultiFieldPanel(
            [FieldPanel("start_year"), FieldPanel("end_year")],
            heading="Years",
        ),
        FieldPanel("blurb"),
        InlinePanel("bullets", heading="Bullet points", label="Bullet"),
        FieldPanel("order"),
    ]


class ExperienceBullet(models.Model):
    experience = ParentalKey(
        Experience, on_delete=models.CASCADE, related_name="bullets"
    )
    text = models.CharField(max_length=300)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Experience bullet"
        verbose_name_plural = "Experience bullets"

    def __str__(self):
        return self.text


LANGUAGE_LEVEL_CHOICES = [
    ("native",       "Native"),
    ("fluent",       "Fluent"),
    ("advanced",     "Advanced"),
    ("intermediate", "Intermediate"),
    ("basic",        "Basic"),
]


class Grant(models.Model):
    title          = models.CharField(max_length=300)
    funder         = models.CharField(max_length=200)
    role           = models.CharField(max_length=100, blank=True, help_text="e.g. Principal Investigator, Co-Investigator.")
    amount         = models.CharField(max_length=60, blank=True, help_text="e.g. €50,000")
    start_year     = models.PositiveIntegerField(null=True, blank=True)
    end_year       = models.PositiveIntegerField(null=True, blank=True)
    description    = models.TextField(blank=True)
    url            = models.URLField(blank=True)
    orcid_put_code = models.CharField(max_length=50, blank=True, db_index=True)
    order          = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-start_year", "order", "id"]
        verbose_name = "Grant"
        verbose_name_plural = "Grants"

    def __str__(self):
        return f"{self.title} ({self.funder})"

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("title"),
                FieldPanel("funder"),
                FieldPanel("role"),
                FieldPanel("amount"),
                FieldPanel("start_year"),
                FieldPanel("end_year"),
            ],
            heading="Grant",
        ),
        MultiFieldPanel(
            [FieldPanel("description"), FieldPanel("url")],
            heading="Details",
        ),
        FieldPanel("orcid_put_code"),
        FieldPanel("order"),
    ]


class Award(models.Model):
    title       = models.CharField(max_length=300)
    issuer      = models.CharField(max_length=200)
    year        = models.PositiveIntegerField(null=True, blank=True)
    description = models.TextField(blank=True)
    url         = models.URLField(blank=True)
    order       = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-year", "order", "id"]
        verbose_name = "Award / Honour"
        verbose_name_plural = "Awards & Honours"

    def __str__(self):
        return f"{self.title} — {self.issuer}"

    panels = [
        FieldPanel("title"),
        FieldPanel("issuer"),
        FieldPanel("year"),
        FieldPanel("description"),
        FieldPanel("url"),
        FieldPanel("order"),
    ]


class Language(models.Model):
    name       = models.CharField(max_length=80)
    level      = models.CharField(max_length=20, choices=LANGUAGE_LEVEL_CHOICES, default="fluent")
    order      = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Language"
        verbose_name_plural = "Languages"

    def __str__(self):
        return f"{self.name} ({self.get_level_display()})"

    panels = [
        FieldPanel("name"),
        FieldPanel("level"),
        FieldPanel("order"),
    ]


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
    image = models.ImageField(upload_to=site_upload_to, validators=[validate_image_file])
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


PUB_TYPE_CHOICES = [
    ("journal",      "Journal Article"),
    ("conference",   "Conference Paper"),
    ("preprint",     "Preprint"),
    ("thesis",       "Thesis / Dissertation"),
    ("book_chapter", "Book Chapter"),
    ("other",        "Other"),
]

PUB_TYPE_ORDER = ["journal", "conference", "preprint", "thesis", "book_chapter", "other"]


class Publication(models.Model):
    title          = models.CharField(max_length=500)
    authors        = models.TextField(help_text="Author list as displayed, e.g. 'Correia R, Smith J, Jones A'.")
    highlight_name = models.CharField(
        max_length=100, blank=True,
        help_text="Your name as it appears in authors — will be bolded in the CV.",
    )
    venue          = models.CharField(max_length=300, help_text="Journal or conference name.")
    year           = models.PositiveIntegerField()
    pub_type       = models.CharField(max_length=20, choices=PUB_TYPE_CHOICES, default="journal")
    doi            = models.CharField(max_length=150, blank=True)
    url            = models.URLField(blank=True)
    abstract       = models.TextField(blank=True)
    orcid_put_code = models.CharField(max_length=50, blank=True, db_index=True)
    citation_count = models.IntegerField(default=0)
    featured       = models.BooleanField(default=False)
    order          = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-year", "order", "id"]
        verbose_name = "Publication"
        verbose_name_plural = "Publications"

    def __str__(self):
        return f"({self.year}) {self.title[:80]}"

    @property
    def authors_display(self):
        """Return authors string with highlight_name wrapped in <strong>."""
        if not self.highlight_name:
            return self.authors
        return self.authors.replace(self.highlight_name, f"<strong>{self.highlight_name}</strong>", 1)

    @property
    def link(self):
        if self.doi:
            return f"https://doi.org/{self.doi}"
        return self.url

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("title"),
                FieldPanel("authors"),
                FieldPanel("highlight_name"),
                FieldPanel("venue"),
                FieldPanel("year"),
                FieldPanel("pub_type"),
            ],
            heading="Publication",
        ),
        MultiFieldPanel(
            [FieldPanel("doi"), FieldPanel("url")],
            heading="Links",
        ),
        MultiFieldPanel(
            [
                FieldPanel("abstract"),
                FieldPanel("citation_count"),
                FieldPanel("featured"),
                FieldPanel("order"),
            ],
            heading="Details",
        ),
        FieldPanel("orcid_put_code"),
    ]


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
        verbose_name = "Skill"
        verbose_name_plural = "Skills"

    def __str__(self):
        return self.name

    panels = [
        FieldPanel("name"),
        FieldPanel("description"),
        FieldPanel("icon"),
        FieldPanel("order"),
        FieldPanel("active"),
    ]


# ---------- portfolio ----------
# BACKWARDS COMPATIBLE DO NOT REMOVE
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