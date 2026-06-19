from __future__ import annotations

from django.conf import settings
from django.db import models
from django.shortcuts import redirect

from modelcluster.fields import ParentalKey
from modelcluster.tags import ClusterTaggableManager
from taggit.models import TaggedItemBase

from wagtail import blocks
from wagtail.api import APIField
from wagtail.images.api.fields import ImageRenditionField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, ObjectList, TabbedInterface
from wagtail.embeds.blocks import EmbedBlock
from wagtail.fields import StreamField
from wagtail.images import get_image_model_string
from wagtail.images.blocks import ImageChooserBlock
from wagtail.models import Page, PageManager
from wagtail.search import index

from wagtail_headless_preview.models import HeadlessMixin, HeadlessServeMixin
from wagtail.documents.blocks import DocumentChooserBlock


def frontend_url(path: str = "/") -> str:
    """Absolute URL on the public Next.js frontend (for headless redirects)."""
    base = getattr(settings, "FRONTEND_BASE_URL", "http://localhost:8000").rstrip("/")
    return base + path


# =============================================================================
# Shared StreamField blocks (used by BlogPage + PortfolioProjectPage)
# =============================================================================

def _image_api_rep(image, alt_override=None):
    """Serialise a Wagtail image to self-contained rendition URLs for the API."""
    if not image:
        return None
    full = image.get_rendition("width-1600")
    thumb = image.get_rendition("fill-600x400")
    return {
        "id": image.id,
        "title": image.title,
        "alt": alt_override or image.title,
        "url": full.url,
        "width": full.width,
        "height": full.height,
        "thumb": thumb.url,
    }


class PrettyEmbedBlock(blocks.StructBlock):
    """Embed with presentation controls (matches your existing blog embed block)."""

    url = EmbedBlock(required=True)
    caption = blocks.TextBlock(required=False, rows=4)

    width = blocks.ChoiceBlock(
        required=False,
        choices=[
            ("sm", "Small"),
            ("md", "Medium"),
            ("lg", "Large"),
            ("full", "Full width"),
        ],
        default="md",
    )

    align = blocks.ChoiceBlock(
        required=False,
        choices=[
            ("center", "Center"),
            ("left", "Left"),
            ("right", "Right"),
        ],
        default="center",
    )

    style = blocks.ChoiceBlock(
        required=False,
        choices=[
            ("plain", "Plain"),
            ("card", "Card"),
            ("soft", "Soft panel"),
        ],
        default="card",
    )

    class Meta:
        icon = "media"
        label = "Embed"


class PrettyImageBlock(blocks.StructBlock):
    """Image block with your presentation controls (used by both pages)."""

    image = ImageChooserBlock(required=True)
    caption = blocks.TextBlock(required=False, rows=4)

    alignment = blocks.ChoiceBlock(
        choices=[
            ("center", "Center"),
            ("wide", "Wide"),
            ("full", "Full width"),
            ("left", "Left (wrap)"),
            ("right", "Right (wrap)"),
        ],
        default="center",
        required=True,
    )

    style = blocks.ChoiceBlock(
        required=False,
        choices=[
            ("plain", "Plain"),
            ("card", "Card"),
            ("soft", "Soft panel"),
            ("frame", "Framed"),
        ],
        default="plain",
    )

    width_pct = blocks.IntegerBlock(
        required=False,
        default=100,
        min_value=20,
        max_value=100,
        help_text="Width as % of content column (20–100). Ignored for Full/Wide alignment.",
    )

    radius = blocks.ChoiceBlock(
        required=False,
        choices=[
            ("none", "None"),
            ("sm", "Small"),
            ("md", "Medium"),
            ("lg", "Large"),
        ],
        default="lg",
    )

    shadow = blocks.ChoiceBlock(
        required=False,
        choices=[
            ("none", "None"),
            ("sm", "Soft"),
            ("md", "Medium"),
        ],
        default="sm",
    )

    aspect = blocks.ChoiceBlock(
        required=False,
        choices=[
            ("auto", "Original"),
            ("16x9", "16:9"),
            ("4x3", "4:3"),
            ("1x1", "1:1"),
        ],
        default="auto",
        help_text="Optional crop/aspect (uses Wagtail renditions).",
    )

    link_url = blocks.URLBlock(required=False, help_text="Optional: make image clickable.")
    open_in_new = blocks.BooleanBlock(required=False, default=False)
    alt_override = blocks.CharBlock(required=False, max_length=160, help_text="Optional: override alt text.")

    def get_api_representation(self, value, context=None):
        rep = super().get_api_representation(value, context)
        rep["image"] = _image_api_rep(value.get("image"), value.get("alt_override"))
        return rep
    caption_spacing = blocks.ChoiceBlock(
        required=False,
        choices=[
            ("sm", "Small"),
            ("md", "Medium"),
            ("lg", "Large"),
        ],
        default="sm",
        help_text="Space between the image and its caption.",
    )

    class Meta:
        icon = "image"
        label = "Image"


class HeadingBlock(blocks.StructBlock):
    level = blocks.ChoiceBlock(
        choices=[("h2", "H2"), ("h3", "H3"), ("h4", "H4")],
        default="h2",
    )
    text = blocks.CharBlock()

    class Meta:
        icon = "title"


class AlignedParagraphBlock(blocks.StructBlock):
    text = blocks.RichTextBlock(
        features=["bold", "italic", "link", "ol", "ul", "hr", "blockquote", "code"],
    )
    alignment = blocks.ChoiceBlock(
        choices=[
            ("justify", "Justified"),
            ("left", "Left"),
            ("center", "Center"),
            ("right", "Right"),
        ],
        default="justify",
    )

    class Meta:
        icon = "doc-full"
        label = "Paragraph (aligned)"


class CalloutBlock(blocks.StructBlock):
    style = blocks.ChoiceBlock(
        choices=[("info", "Info"), ("tip", "Tip"), ("warn", "Warning"), ("note", "Note")],
        default="info",
    )
    title = blocks.CharBlock(required=False)
    text = blocks.RichTextBlock(features=["bold", "italic", "link", "ol", "ul"])

    class Meta:
        icon = "placeholder"
        label = "Callout"


class CodeBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=False, help_text="Optional: filename or label")
    language = blocks.ChoiceBlock(
        choices=[
            ("python", "Python"),
            ("bash", "Bash"),
            ("json", "JSON"),
            ("yaml", "YAML"),
            ("sql", "SQL"),
            ("javascript", "JavaScript"),
            ("html", "HTML"),
            ("css", "CSS"),
            ("r", "R"),
            ("text", "Plain text"),
        ],
        default="text",
    )
    style = blocks.ChoiceBlock(
        choices=[
            ("default", "Default"),
            ("card", "Card (elevated)"),
            ("terminal", "Terminal"),
        ],
        default="default",
        required=False,
    )
    code = blocks.TextBlock(rows=12)

    class Meta:
        icon = "code"
        label = "Code block"


class ButtonBlock(blocks.StructBlock):
    text = blocks.CharBlock(required=True, max_length=80)
    url = blocks.URLBlock(required=True)
    variant = blocks.ChoiceBlock(
        choices=[("primary", "Primary"), ("outline", "Outline"), ("link", "Link")],
        default="primary",
    )

    class Meta:
        icon = "link"
        label = "Button"


class DividerBlock(blocks.StaticBlock):
    class Meta:
        icon = "horizontalrule"
        label = "Divider"


class SpacerBlock(blocks.ChoiceBlock):
    def __init__(self, *args, **kwargs):
        super().__init__(
            choices=[("sm", "Small"), ("md", "Medium"), ("lg", "Large")],
            default="md",
            *args,
            **kwargs,
        )

    class Meta:
        icon = "arrows-up-down"
        label = "Spacer"


class GalleryBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=False, max_length=120)
    width_pct = blocks.IntegerBlock(
        required=False,
        default=100,
        min_value=20,
        max_value=100,
        help_text="Width as % of content column (20–100).",
    )
    autoplay = blocks.BooleanBlock(
        required=False,
        default=True,
        help_text="Auto-advance slides every 4 seconds.",
    )
    images = blocks.ListBlock(ImageChooserBlock())

    def get_api_representation(self, value, context=None):
        rep = super().get_api_representation(value, context)
        rep["images"] = [_image_api_rep(img) for img in value.get("images") or []]
        return rep

    class Meta:
        icon = "image"
        label = "Gallery"

class PdfItemBlock(blocks.StructBlock):
    document = DocumentChooserBlock(required=True)
    label = blocks.CharBlock(required=False, max_length=60, help_text="Optional button label (e.g. Poster, PDF, Report)")
    note = blocks.CharBlock(required=False, max_length=120, help_text="Optional small text under the button")
    open_in_new = blocks.BooleanBlock(required=False, default=True)

    class Meta:
        icon = "doc-full-inverse"
        label = "PDF"


class PdfDownloadsBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=False, max_length=80)
    description = blocks.CharBlock(required=False, max_length=180)

    documents = blocks.ListBlock(
        PdfItemBlock(),
        min_num=1,
        max_num=4,
        help_text="Add 1–4 PDFs (e.g. poster, report, appendix, slides).",
    )

    def get_api_representation(self, value, context=None):
        rep = super().get_api_representation(value, context)
        items = []
        for d in value.get("documents") or []:
            doc = d.get("document")
            if not doc:
                continue
            items.append({
                "label": d.get("label") or doc.title,
                "note": d.get("note") or "",
                "open_in_new": bool(d.get("open_in_new")),
                "url": doc.url,          # relative /documents/<id>/<file> — proxied
                "filename": doc.filename,
            })
        rep["documents"] = items
        return rep

    class Meta:
        icon = "doc-full-inverse"
        label = "PDF downloads"
        
class SectionInnerStream(blocks.StreamBlock):
    heading = HeadingBlock()
    paragraph = AlignedParagraphBlock()
    image = PrettyImageBlock()
    quote = blocks.BlockQuoteBlock(icon="openquote")
    embed = PrettyEmbedBlock()
    callout = CalloutBlock()
    code = CodeBlock()
    button = ButtonBlock()
    divider = DividerBlock()
    spacer = SpacerBlock()
    gallery = GalleryBlock()
    pdfs = PdfDownloadsBlock()

    class Meta:
        label = "Section content"
        required = False


class SectionBlock(blocks.StructBlock):
    background = blocks.ChoiceBlock(
        choices=[("none", "None"), ("soft", "Soft"), ("contrast", "Contrast")],
        default="none",
    )
    inner = SectionInnerStream()

    class Meta:
        icon = "placeholder"
        label = "Section"

class BodyStream(blocks.StreamBlock):
    """
    Canonical body block set used by BOTH BlogPage and PortfolioProjectPage.
    This matches your BlogPage set + your newer blocks.
    """

    heading = HeadingBlock()
    paragraph = AlignedParagraphBlock()
    image = PrettyImageBlock()
    quote = blocks.BlockQuoteBlock(icon="openquote")
    embed = PrettyEmbedBlock()
    callout = CalloutBlock()
    code = CodeBlock()
    button = ButtonBlock()
    divider = DividerBlock()
    spacer = SpacerBlock()
    gallery = GalleryBlock()
    section = SectionBlock()
    pdfs = PdfDownloadsBlock()


    class Meta:
        label = "Body content"
        required = False


# =============================================================================
# Blog
# =============================================================================

class BlogPageTag(TaggedItemBase):
    content_object = ParentalKey(
        "cms.BlogPage",
        related_name="tagged_items",
        on_delete=models.CASCADE,
    )


class BlogIndexPage(HeadlessServeMixin, Page):
    # Headless: the blog list lives on the Next.js frontend. The backend page is
    # just a container; both serve and preview redirect there (no Django render).
    max_count = 1
    parent_page_types = ["cms.HomePage"]
    subpage_types = ["cms.BlogPage"]

    def serve_preview(self, request, mode_name):
        return redirect(frontend_url("/blog"))


class BlogPage(HeadlessMixin, Page):
    objects = PageManager()

    date = models.DateField("Post date", db_index=True)
    intro = models.CharField(max_length=250, blank=True)

    featured = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Mark as featured (useful for homepage / blog index highlights).",
    )

    reading_time_minutes = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        help_text="Optional: show an estimated read time (minutes).",
    )

    hero_image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Optional header image.",
    )

    hero_caption = models.CharField(
        max_length=200,
        blank=True,
        help_text="Optional caption under the hero image.",
    )

    card_image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Thumbnail shown on the blog index card. Falls back to the hero image.",
    )

    tags = ClusterTaggableManager(through=BlogPageTag, blank=True)

    body = StreamField(
        BodyStream(),
        use_json_field=True,
        blank=True,
    )

    search_fields = Page.search_fields + [
        index.SearchField("title", partial_match=True),
        index.SearchField("intro", partial_match=True),
        index.SearchField("body"),
        index.FilterField("date"),
        index.FilterField("featured"),
    ]

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("date"),
                FieldPanel("featured"),
                FieldPanel("reading_time_minutes"),
            ],
            heading="Post settings",
        ),
        FieldPanel("intro"),
        FieldPanel("body"),
    ]

    metadata_panels = [
        MultiFieldPanel(
            [
                FieldPanel("hero_image"),
                FieldPanel("hero_caption"),
                FieldPanel("card_image"),
            ],
            heading="Hero",
        ),
        FieldPanel("tags"),
    ]

    promote_panels = Page.promote_panels

    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Content"),
            ObjectList(metadata_panels, heading="Metadata"),
            ObjectList(promote_panels, heading="Promote"),
            ObjectList(Page.settings_panels, heading="Settings"),
        ]
    )

    @property
    def tag_names(self):
        return [t.name for t in self.tags.all()]

    api_fields = [
        APIField("intro"),
        APIField("date"),
        APIField("featured"),
        APIField("reading_time_minutes"),
        APIField("hero_caption"),
        APIField("hero_image", serializer=ImageRenditionField("width-1200")),
        APIField("hero_thumb", serializer=ImageRenditionField("fill-600x400", source="hero_image")),
        APIField("card_thumb", serializer=ImageRenditionField("fill-800x800", source="card_image")),
        APIField("body"),
        APIField("tag_names"),
    ]

    class Meta:
        verbose_name = "Blog post"


# =============================================================================
# Portfolio
# =============================================================================

class PortfolioPageTag(TaggedItemBase):
    content_object = ParentalKey(
        "cms.PortfolioProjectPage",
        related_name="tagged_items",
        on_delete=models.CASCADE,
    )


class PortfolioIndexPage(HeadlessServeMixin, Page):
    # Headless: the project list lives on the Next.js frontend. Both serve and
    # preview redirect there (no Django render).
    max_count = 1
    parent_page_types = ["cms.HomePage"]
    subpage_types = ["cms.PortfolioProjectPage"]

    intro = models.CharField(max_length=250, blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
    ]

    api_fields = [APIField("intro")]

    def serve_preview(self, request, mode_name):
        return redirect(frontend_url("/portfolio"))


class PortfolioProjectPage(HeadlessMixin, Page):
    parent_page_types = ["cms.PortfolioIndexPage"]
    subpage_types = []

    subtitle = models.CharField(max_length=160, blank=True)

    cover_image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    card_image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Square thumbnail shown on the work list. Falls back to the cover image.",
    )

    external_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)

    tags = ClusterTaggableManager(through=PortfolioPageTag, blank=True)

    # ✅ Upgraded: same body capabilities as BlogPage
    body = StreamField(
        BodyStream(),
        blank=True,
        use_json_field=True,
    )

    search_fields = Page.search_fields + [
        index.SearchField("title", partial_match=True),
        index.SearchField("subtitle", partial_match=True),
        index.SearchField("body"),
    ]

    content_panels = Page.content_panels + [
        FieldPanel("subtitle"),
        FieldPanel("cover_image"),
        FieldPanel("card_image"),
        MultiFieldPanel(
            [
                FieldPanel("external_url"),
                FieldPanel("github_url"),
            ],
            heading="Links",
        ),
        FieldPanel("tags"),
        FieldPanel("body"),
    ]

    @property
    def tag_names(self):
        return [t.name for t in self.tags.all()]

    api_fields = [
        APIField("subtitle"),
        APIField("external_url"),
        APIField("github_url"),
        APIField("cover_image", serializer=ImageRenditionField("width-1200")),
        APIField("cover_thumb", serializer=ImageRenditionField("fill-800x600", source="cover_image")),
        APIField("card_thumb", serializer=ImageRenditionField("fill-800x800", source="card_image")),
        APIField("body"),
        APIField("tag_names"),
    ]

    class Meta:
        verbose_name = "Portfolio project"


# =============================================================================
# Home
# =============================================================================

# ---------------------------------------------------------------------------
# Home page sections — a CMS-controlled, reorderable list of homepage sections.
#
# Marker sections (about/skills/timeline/work/research/contact) draw their
# content from the CV snippets / SiteBundle; the block only controls presence,
# order and an optional heading override, and (unlike gallery/carousel) appears
# in the navbar. Gallery and carousel carry their own content and stay out of
# the nav.
# ---------------------------------------------------------------------------


class _MarkerSectionBlock(blocks.StructBlock):
    """A content section whose data comes from the SiteBundle; the block just
    toggles it on and optionally overrides its heading."""

    title = blocks.CharBlock(
        required=False,
        max_length=120,
        help_text="Optional heading override (defaults to the standard title).",
    )


class HomeGalleryImageBlock(blocks.StructBlock):
    image = ImageChooserBlock(required=True)
    caption = blocks.CharBlock(required=False, max_length=160)


class HomeGalleryBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=False, max_length=120, default="Gallery")
    intro = blocks.CharBlock(required=False, max_length=240)
    items = blocks.ListBlock(HomeGalleryImageBlock())

    def get_api_representation(self, value, context=None):
        rep = super().get_api_representation(value, context)
        rep["items"] = [
            {"image": _image_api_rep(it.get("image")), "caption": it.get("caption") or ""}
            for it in value.get("items") or []
        ]
        return rep

    class Meta:
        icon = "image"
        label = "Gallery section"


class HomeCarouselSlideBlock(blocks.StructBlock):
    image = ImageChooserBlock(required=True)
    caption = blocks.CharBlock(required=False, max_length=160)
    link = blocks.URLBlock(required=False)


class HomeCarouselBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=False, max_length=120)
    intro = blocks.CharBlock(required=False, max_length=240)
    autoplay = blocks.BooleanBlock(
        required=False, default=True, help_text="Auto-advance every 5 seconds."
    )
    slides = blocks.ListBlock(HomeCarouselSlideBlock())

    def get_api_representation(self, value, context=None):
        rep = super().get_api_representation(value, context)
        rep["slides"] = [
            {
                "image": _image_api_rep(s.get("image")),
                "caption": s.get("caption") or "",
                "link": s.get("link") or "",
            }
            for s in value.get("slides") or []
        ]
        return rep

    class Meta:
        icon = "image"
        label = "Carousel section"


class HomeSectionStream(blocks.StreamBlock):
    about = _MarkerSectionBlock(icon="user", label="About")
    skills = _MarkerSectionBlock(icon="cog", label="Skills")
    timeline = _MarkerSectionBlock(icon="list-ul", label="Timeline")
    work = _MarkerSectionBlock(icon="folder-open-inverse", label="Work / Projects")
    research = _MarkerSectionBlock(icon="doc-full", label="Research / Publications")
    contact = _MarkerSectionBlock(icon="mail", label="Contact")
    gallery = HomeGalleryBlock()
    carousel = HomeCarouselBlock()

    class Meta:
        block_counts = {
            "about": {"max_num": 1},
            "skills": {"max_num": 1},
            "timeline": {"max_num": 1},
            "work": {"max_num": 1},
            "research": {"max_num": 1},
            "contact": {"max_num": 1},
        }


class HomePage(HeadlessMixin, Page):
    max_count = 1
    subpage_types = ["cms.BlogIndexPage", "cms.PortfolioIndexPage"]

    intro = models.CharField(
        max_length=250,
        blank=True,
        help_text="Optional short intro text for the homepage",
    )

    sections = StreamField(
        HomeSectionStream(),
        use_json_field=True,
        blank=True,
        help_text=(
            "The homepage sections, in order. Add/remove sections to control "
            "what shows and the navbar; gallery and carousel stay out of the nav."
        ),
    )

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("sections"),
    ]

    api_fields = [APIField("intro"), APIField("sections")]
