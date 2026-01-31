from django.db import models
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render

from modelcluster.fields import ParentalKey
from modelcluster.tags import ClusterTaggableManager

from taggit.models import TaggedItemBase

from wagtail import blocks
from wagtail.fields import StreamField
from wagtail.models import Page, PageManager
from wagtail.search import index
from wagtail.admin.panels import (
    FieldPanel,
    MultiFieldPanel,
    ObjectList,
    TabbedInterface,
)

from django.core.paginator import Paginator

from wagtail.images.blocks import ImageChooserBlock
from wagtail.images import get_image_model_string
from wagtail.embeds.blocks import EmbedBlock
from wagtail.contrib.routable_page.models import RoutablePageMixin, route


# ----------------------------
# Tags
# ----------------------------
class BlogPageTag(TaggedItemBase):
    content_object = ParentalKey(
        "cms.BlogPage",
        related_name="tagged_items",
        on_delete=models.CASCADE,
    )


# ----------------------------
# Index Page
# ----------------------------
class BlogIndexPage(RoutablePageMixin, Page):
    max_count = 1
    subpage_types = ["cms.BlogPage"]

    # Optional: limit in admin what can be added under index
    parent_page_types = ["cms.HomePage"]

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

        # Pick featured post (explicit), fallback to latest
        featured_post = qs.filter(featured=True).first()
        if featured_post is None:
            featured_post = qs.first()

        # Remove featured from list so it doesn't appear twice
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


# ----------------------------
# Blog Page
# ----------------------------
class BlogPage(Page):
    objects = PageManager()

    # Core content
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
        [
            ("heading", blocks.CharBlock(form_classname="title", icon="title")),
            (
                "paragraph",
                blocks.RichTextBlock(
                    features=[
                        "h2",
                        "h3",
                        "bold",
                        "italic",
                        "link",
                        "ol",
                        "ul",
                        "hr",
                        "blockquote",
                        "code",
                    ],
                    icon="doc-full",
                ),
            ),
            (
                "image",
                blocks.StructBlock(
                    [
                        ("image", ImageChooserBlock(required=True)),
                        ("caption", blocks.CharBlock(required=False)),
                        (
                            "alignment",
                            blocks.ChoiceBlock(
                                choices=[
                                    ("center", "Center"),
                                    ("wide", "Wide"),
                                    ("full", "Full width"),
                                    ("left", "Left (wrap)"),
                                    ("right", "Right (wrap)"),
                                ],
                                default="center",
                                required=True,
                            ),
                        ),
                    ],
                    icon="image",
                    label="Image",
                    template="cms/blocks/image.html",
                ),
            ),
            ("quote", blocks.BlockQuoteBlock(icon="openquote")),
            ("embed", EmbedBlock(icon="media")),
            (
                "callout",
                blocks.StructBlock(
                    [
                        (
                            "style",
                            blocks.ChoiceBlock(
                                choices=[
                                    ("info", "Info"),
                                    ("tip", "Tip"),
                                    ("warn", "Warning"),
                                    ("note", "Note"),
                                ],
                                default="info",
                            ),
                        ),
                        ("title", blocks.CharBlock(required=False)),
                        (
                            "text",
                            blocks.RichTextBlock(features=["bold", "italic", "link", "ol", "ul"]),
                        ),
                    ],
                    icon="placeholder",
                    label="Callout",
                ),
            ),
            (
                "code",
                blocks.StructBlock(
                    [
                        ("title", blocks.CharBlock(required=False, help_text="Optional: filename or label")),
                        (
                            "language",
                            blocks.ChoiceBlock(
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
                            ),
                        ),
                        ("code", blocks.TextBlock(rows=12)),
                    ],
                    icon="code",
                    label="Code block",
                ),
            ),
        ],
        use_json_field=True,
        blank=True,
    )

    # --- Search (nice upgrade) ---
    search_fields = Page.search_fields + [
        index.SearchField("title", partial_match=True),
        index.SearchField("intro", partial_match=True),
        index.SearchField("body"),
        index.FilterField("date"),
        index.FilterField("featured"),
    ]

    # --- Panels grouped nicely ---
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

    promote_panels = Page.promote_panels + [
        # Page.promote_panels already includes slug/seo_title/search_description/etc.
        # Keep it, and optionally add more promote fields later.
    ]

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


# ----------------------------
# Portfolio (Wagtail)
# ----------------------------
from wagtail.snippets.models import register_snippet


class PortfolioPageTag(TaggedItemBase):
    content_object = ParentalKey(
        "cms.PortfolioProjectPage",
        related_name="tagged_items",
        on_delete=models.CASCADE,
    )


class PortfolioIndexPage(RoutablePageMixin, Page):
    max_count = 1
    subpage_types = ["cms.PortfolioProjectPage"]
    parent_page_types = ["cms.HomePage"]

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
        # same listing view, but prettier URL
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

    body = StreamField(
        [
            ("heading", blocks.CharBlock(form_classname="title", icon="title")),
            ("paragraph", blocks.RichTextBlock(features=["bold", "italic", "link", "ol", "ul"])),
            ("image", ImageChooserBlock()),
            ("embed", EmbedBlock(icon="media")),
            ("code", blocks.RawHTMLBlock(icon="code", help_text="Paste highlighted HTML if needed.")),
        ],
        blank=True,
        use_json_field=True,
    )

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


# homepage
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