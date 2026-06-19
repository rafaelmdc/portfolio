# main/models.py
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.text import slugify

import os, uuid
from .validators import validate_image_file

from modelcluster.models import ClusterableModel
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, InlinePanel
from wagtail.contrib.settings.models import BaseGenericSetting, register_setting


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


# ---------- consolidated site content (Wagtail settings) ----------
# (Legacy SiteCopy / SiteAsset key-value models were removed once their data was
#  migrated into SiteContent below; site_upload_to is kept for old migrations.)
@register_setting
class SiteContent(BaseGenericSetting):
    """
    Single global home for the editable copy + profile images that used to live
    in the SiteCopy / SiteAsset key-value tables. Edited under Wagtail
    Settings → Site content. Profile images are Wagtail images (renditions).
    """

    about_title          = models.CharField(max_length=200, blank=True, default="About")
    about_lead           = models.TextField(blank=True)
    about_intro_headline = models.CharField(max_length=300, blank=True)
    about_intro_body     = models.TextField(blank=True)
    about_quote          = models.TextField(blank=True)
    skills_title         = models.CharField(max_length=200, blank=True, default="Skills")
    skills_lead          = models.TextField(blank=True)

    # Personal / contact identity — feeds the CV PDF and the contact section.
    full_name    = models.CharField(max_length=120, blank=True, default="Rafael Correia")
    role_title   = models.CharField(
        max_length=160, blank=True, default="Software Developer & Researcher",
        help_text="Headline role, shown on the CV.",
    )
    email        = models.EmailField(blank=True, default="rafaelmdcorreia@gmail.com")
    linkedin_url = models.URLField(
        blank=True,
        default="https://linkedin.com/in/rafael-alexandre-correia-2b8a33213",
    )

    github_username      = models.CharField(
        max_length=100, blank=True,
        help_text="GitHub username, used to show live repo/stars stats.",
    )

    # ---- Hero copy (all editable, with sensible defaults) ----
    hero_eyebrow   = models.CharField(
        max_length=200, blank=True, default="MSc Bioinformatics · biology ∩ data")
    hero_headline  = models.CharField(
        max_length=200, blank=True,
        default="I turn biological questions into reproducible code.")
    hero_highlight = models.CharField(
        max_length=100, blank=True, default="reproducible code.",
        help_text="Part of the headline to highlight (must appear in the headline).")
    hero_cta_primary   = models.CharField(max_length=60, blank=True, default="View selected work")
    hero_cta_secondary = models.CharField(max_length=60, blank=True, default="Timeline & CV")

    # ---- Contact copy + which buttons show ----
    contact_headline = models.CharField(
        max_length=200, blank=True,
        default="Let's turn biology into something runnable.")
    contact_note = models.CharField(
        max_length=200, blank=True,
        default="always happy to talk research, code, or collaboration")
    contact_show_email    = models.BooleanField(default=True)
    contact_show_github   = models.BooleanField(default=True)
    contact_show_linkedin = models.BooleanField(default=True)
    contact_show_blog     = models.BooleanField(default=True)

    # ---- About "at a glance" stats — each row toggleable ----
    about_focus = models.CharField(
        max_length=120, blank=True, default="bioinformatics · genomics",
        help_text="Value shown for the 'focus' row.")
    stat_focus        = models.BooleanField(default=True, verbose_name="Show focus")
    stat_repos        = models.BooleanField(default=False, verbose_name="Show public repos")
    stat_stars        = models.BooleanField(default=True, verbose_name="Show total stars")
    stat_language     = models.BooleanField(default=True, verbose_name="Show top language")
    stat_followers    = models.BooleanField(default=False, verbose_name="Show followers")
    stat_commits      = models.BooleanField(default=True, verbose_name="Show commits")
    stat_publications = models.BooleanField(default=True, verbose_name="Show publications")
    stat_honors       = models.BooleanField(default=False, verbose_name="Show honors")

    # ---- CV PDF (auto-generated into a Wagtail Document, cached) ----
    CV_REFRESH_CHOICES = [("daily", "Daily"), ("weekly", "Weekly")]
    cv_enabled = models.BooleanField(
        default=True, help_text="Show the 'Open CV' button on the site.",
    )
    cv_refresh = models.CharField(
        max_length=10, choices=CV_REFRESH_CHOICES, default="weekly",
        help_text="How often the CV PDF is regenerated from your CMS data.",
    )
    cv_document = models.ForeignKey(
        "wagtaildocs.Document", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="+",
        help_text="Auto-generated CV PDF. Managed automatically — no need to set this.",
    )
    cv_generated_at = models.DateTimeField(null=True, blank=True, editable=False)

    about_profile = models.ForeignKey(
        "wagtailimages.Image", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="+",
    )
    home_profile = models.ForeignKey(
        "wagtailimages.Image", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="+",
    )

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("about_title"),
                FieldPanel("about_lead"),
                FieldPanel("about_intro_headline"),
                FieldPanel("about_intro_body"),
                FieldPanel("about_quote"),
            ],
            heading="About copy",
        ),
        MultiFieldPanel(
            [FieldPanel("skills_title"), FieldPanel("skills_lead")],
            heading="Skills copy",
        ),
        MultiFieldPanel(
            [
                FieldPanel("hero_eyebrow"),
                FieldPanel("hero_headline"),
                FieldPanel("hero_highlight"),
                FieldPanel("hero_cta_primary"),
                FieldPanel("hero_cta_secondary"),
            ],
            heading="Hero copy",
        ),
        MultiFieldPanel(
            [
                FieldPanel("about_focus"),
                FieldPanel("stat_focus"),
                FieldPanel("stat_repos"),
                FieldPanel("stat_stars"),
                FieldPanel("stat_language"),
                FieldPanel("stat_followers"),
                FieldPanel("stat_commits"),
                FieldPanel("stat_publications"),
                FieldPanel("stat_honors"),
            ],
            heading="About — at-a-glance stats",
        ),
        MultiFieldPanel(
            [
                FieldPanel("contact_headline"),
                FieldPanel("contact_note"),
                FieldPanel("contact_show_email"),
                FieldPanel("contact_show_github"),
                FieldPanel("contact_show_linkedin"),
                FieldPanel("contact_show_blog"),
            ],
            heading="Contact section",
        ),
        MultiFieldPanel(
            [FieldPanel("about_profile"), FieldPanel("home_profile")],
            heading="Profile images",
        ),
        MultiFieldPanel(
            [
                FieldPanel("full_name"),
                FieldPanel("role_title"),
                FieldPanel("email"),
                FieldPanel("linkedin_url"),
                FieldPanel("github_username"),
            ],
            heading="Personal / contact",
        ),
        MultiFieldPanel(
            [
                FieldPanel("cv_enabled"),
                FieldPanel("cv_refresh"),
                FieldPanel("cv_document", read_only=True),
            ],
            heading="CV PDF",
        ),
    ]

    class Meta:
        verbose_name = "Site content"


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