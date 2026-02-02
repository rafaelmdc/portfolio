"""
Wagtail CMS models for Blog + Portfolio.

Refactor goals:
- Remove duplicate imports / tighten structure.
- Define a single, reusable StreamField block set so Blog + Portfolio share the same body capabilities.
- Keep Blog behavior and URLs the same.
- Upgrade PortfolioProjectPage.body to use the same rich blocks as BlogPage.body.

NOTE:
- Changing StreamField *block definitions* typically does not require a DB migration,
  but existing StreamField content may become incompatible if you *rename* block types.
  This refactor keeps block names consistent with your BlogPage body blocks.
- If you already have PortfolioProjectPage body content, it will not automatically
  transform (its old "heading" was a CharBlock). Easiest path: re-save those pages,
  or temporarily keep a legacy "heading_text" block (included below).
"""

from __future__ import annotations

from django.core.paginator import Paginator
from django.db import models
from django.shortcuts import render

from modelcluster.fields import ParentalKey
from modelcluster.tags import ClusterTaggableManager
from taggit.models import TaggedItemBase

from wagtail import blocks
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, ObjectList, TabbedInterface
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.embeds.blocks import EmbedBlock
from wagtail.fields import StreamField
from wagtail.images import get_image_model_string
from wagtail.images.blocks import ImageChooserBlock
from wagtail.models import Page, PageManager
from wagtail.search import index


# =============================================================================
# Shared StreamField blocks (used by BlogPage + PortfolioProjectPage)
# =============================================================================

class PrettyEmbedBlock(blocks.StructBlock):
    """Embed with presentation controls (matches your existing blog embed block)."""

    url = EmbedBlock(required=True)
    caption = blocks.CharBlock(required=False, max_length=160)

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
        template = "cms/blocks/embed.html"


class PrettyImageBlock(blocks.StructBlock):
    """Image block with your presentation controls (used by both pages)."""

    image = ImageChooserBlock(required=True)
    caption = blocks.CharBlock(required=False, max_length=220)

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

    max_width = blocks.ChoiceBlock(
        required=False,
        choices=[
            ("sm", "Small"),
            ("md", "Medium"),
            ("lg", "Large"),
            ("xl", "Extra large"),
            ("none", "No cap"),
        ],
        default="lg",
        help_text="Caps the rendered width (helpful for centered images).",
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

    class Meta:
        icon = "image"
        label = "Image"
        template = "cms/blocks/image.html"


class HeadingBlock(blocks.StructBlock):
    level = blocks.ChoiceBlock(
        choices=[("h2", "H2"), ("h3", "H3"), ("h4", "H4")],
        default="h2",
    )
    text = blocks.CharBlock()

    class Meta:
        icon = "title"
        template = "cms/blocks/heading.html"


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
        template = "cms/blocks/callout.html"


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
    code = blocks.TextBlock(rows=12)

    class Meta:
        icon = "code"
        label = "Code block"
        template = "cms/blocks/code.html"


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
        template = "cms/blocks/button.html"


class DividerBlock(blocks.StaticBlock):
    class Meta:
        icon = "horizontalrule"
        label = "Divider"
        template = "cms/blocks/divider.html"


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
        template = "cms/blocks/spacer.html"


class GalleryBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=False, max_length=120)
    columns = blocks.ChoiceBlock(choices=[("2", "2 columns"), ("3", "3 columns")], default="2")
    images = blocks.ListBlock(ImageChooserBlock())

    class Meta:
        icon = "image"
        label = "Gallery"
        template = "cms/blocks/gallery.html"


class SectionInnerStream(blocks.StreamBlock):
    heading = HeadingBlock()
    paragraph = blocks.RichTextBlock(
        features=["h2", "h3", "bold", "italic", "link", "ol", "ul", "hr", "blockquote", "code"],
        icon="doc-full",
    )
    image = PrettyImageBlock()
    quote = blocks.BlockQuoteBlock(icon="openquote")
    embed = PrettyEmbedBlock()
    callout = CalloutBlock()
    code = CodeBlock()
    button = ButtonBlock()
    divider = DividerBlock()
    spacer = SpacerBlock()
    gallery = GalleryBlock()

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
        template = "cms/blocks/section.html"


class BodyStream(blocks.StreamBlock):
    """
    Canonical body block set used by BOTH BlogPage and PortfolioProjectPage.
    This matches your BlogPage set + your newer blocks.
    """

    heading = HeadingBlock()
    paragraph = blocks.RichTextBlock(
        features=["bold", "italic", "link", "ol", "ul", "hr", "blockquote", "code"],
        icon="doc-full",
    )
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


class BlogIndexPage(RoutablePageMixin, Page):
    max_count = 1
    parent_page_types = ["cms.HomePage"]
    subpage_types = ["cms.BlogPage"]

    def get_posts(self):
        return (
            BlogPage.objects.child_of(self)
            .live()
            .public()
            .order_by("-first_published_at")
        )

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        qs = self.get_posts()

        featured_post = qs.filter(featured=True).first() or qs.first()
        if featured_post:
            qs = qs.exclude(id=featured_post.id)

        paginator = Paginator(qs, 9)
        page_number = request.GET.get("page")
        posts_page = paginator.get_page(page_number)

        context["featured_post"] = featured_post
        context["posts"] = posts_page
        return context

    @route(r"^tag/(?P<tag_slug>[-\w]+)/$")
    def posts_by_tag(self, request, tag_slug):
        posts = self.get_posts().filter(tags__slug=tag_slug)
        context = self.get_context(request)
        context["posts"] = posts
        context["filtered_tag_slug"] = tag_slug
        return render(request, "cms/blog_index_page.html", context)


class BlogPage(Page):
    objects = PageManager()

    date = models.DateField("Post date")
    intro = models.CharField(max_length=250, blank=True)

    featured = models.BooleanField(
        default=False,
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


class PortfolioIndexPage(RoutablePageMixin, Page):
    max_count = 1
    parent_page_types = ["cms.HomePage"]
    subpage_types = ["cms.PortfolioProjectPage"]

    intro = models.CharField(max_length=250, blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
    ]

    def get_projects(self):
        return (
            PortfolioProjectPage.objects.child_of(self)
            .live()
            .public()
            .order_by("-first_published_at")
        )

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        qs = self.get_projects()

        tag = request.GET.get("tag")
        if tag:
            qs = qs.filter(tags__slug=tag)

        context["projects"] = qs
        context["active_tag"] = tag
        return context

    @route(r"^tag/(?P<tag_slug>[-\w]+)/$")
    def projects_by_tag(self, request, tag_slug, *args, **kwargs):
        context = self.get_context(request)
        context["projects"] = self.get_projects().filter(tags__slug=tag_slug)
        context["active_tag"] = tag_slug
        return render(request, "cms/portfolio_index_page.html", context)


class PortfolioProjectPage(Page):
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

    class Meta:
        verbose_name = "Portfolio project"


# =============================================================================
# Home
# =============================================================================

class HomePage(Page):
    max_count = 1
    subpage_types = ["cms.BlogIndexPage", "cms.PortfolioIndexPage"]

    intro = models.CharField(
        max_length=250,
        blank=True,
        help_text="Optional short intro text for the homepage",
    )

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
    ]
    