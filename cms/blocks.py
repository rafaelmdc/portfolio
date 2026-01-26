from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock
from wagtail.embeds.blocks import EmbedBlock
from wagtail.contrib.table_block.blocks import TableBlock


RICHTEXT_FEATURES = [
    "h2", "h3", "h4",
    "bold", "italic", "link",
    "ol", "ul",
    "hr", "blockquote",
    "code",
    "image",
    "embed",
]


class CodeBlock(blocks.StructBlock):
    language = blocks.ChoiceBlock(
        choices=[
            ("text", "Plain text"),
            ("python", "Python"),
            ("bash", "Bash"),
            ("json", "JSON"),
            ("yaml", "YAML"),
            ("html", "HTML"),
            ("css", "CSS"),
            ("javascript", "JavaScript"),
            ("sql", "SQL"),
        ],
        default="text",
        required=True,
    )
    code = blocks.TextBlock(rows=10, required=True)

    class Meta:
        template = "cms/blocks/code.html"
        icon = "code"
        label = "Code"


class CalloutBlock(blocks.StructBlock):
    style = blocks.ChoiceBlock(
        choices=[
            ("note", "Note"),
            ("info", "Info"),
            ("success", "Success"),
            ("warning", "Warning"),
            ("danger", "Danger"),
        ],
        default="info",
        required=True,
    )
    title = blocks.CharBlock(required=False, max_length=80)
    text = blocks.RichTextBlock(features=["bold", "italic", "link", "ol", "ul"])

    class Meta:
        template = "cms/blocks/callout.html"
        icon = "warning"
        label = "Callout"


class ButtonBlock(blocks.StructBlock):
    text = blocks.CharBlock(max_length=40)
    url = blocks.URLBlock()
    variant = blocks.ChoiceBlock(
        choices=[
            ("primary", "Primary"),
            ("outline", "Outline"),
            ("link", "Link"),
        ],
        default="outline",
        required=True,
    )

    class Meta:
        template = "cms/blocks/button.html"
        icon = "link"
        label = "Button"


class ImageBlock(blocks.StructBlock):
    image = ImageChooserBlock(required=True)
    caption = blocks.CharBlock(required=False, max_length=160)
    credit = blocks.CharBlock(required=False, max_length=160)

    width = blocks.ChoiceBlock(
        choices=[
            ("content", "Content width"),
            ("wide", "Wide"),
            ("full", "Full width"),
        ],
        default="content",
        required=True,
    )

    align = blocks.ChoiceBlock(
        choices=[
            ("center", "Center"),
            ("left", "Float left"),
            ("right", "Float right"),
        ],
        default="center",
        required=True,
    )

    class Meta:
        template = "cms/blocks/image.html"
        icon = "image"
        label = "Image"


class GalleryBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=False, max_length=80)
    images = blocks.ListBlock(ImageChooserBlock(), min_num=2, max_num=12)
    columns = blocks.ChoiceBlock(
        choices=[("2", "2 columns"), ("3", "3 columns"), ("4", "4 columns")],
        default="3",
        required=True,
    )

    class Meta:
        template = "cms/blocks/gallery.html"
        icon = "image"
        label = "Gallery"


class DividerBlock(blocks.StructBlock):
    class Meta:
        template = "cms/blocks/divider.html"
        icon = "horizontalrule"
        label = "Divider"


class SpacerBlock(blocks.StructBlock):
    size = blocks.ChoiceBlock(
        choices=[("sm", "Small"), ("md", "Medium"), ("lg", "Large")],
        default="md",
        required=True,
    )

    class Meta:
        template = "cms/blocks/spacer.html"
        icon = "arrows-up-down"
        label = "Spacer"


class SectionBlock(blocks.StructBlock):
    background = blocks.ChoiceBlock(
        choices=[
            ("none", "None"),
            ("soft", "Soft surface"),
            ("contrast", "Contrast surface"),
        ],
        default="none",
        required=True,
    )
    inner = blocks.StreamBlock(
        [
            ("rich_text", blocks.RichTextBlock(features=RICHTEXT_FEATURES)),
            ("image", ImageBlock()),
            ("gallery", GalleryBlock()),
            ("embed", EmbedBlock()),
            ("code", CodeBlock()),
            ("table", TableBlock()),
            ("callout", CalloutBlock()),
            ("button", ButtonBlock()),
            ("divider", DividerBlock()),
            ("spacer", SpacerBlock()),
        ],
        use_json_field=True,
        blank=True,
    )

    class Meta:
        template = "cms/blocks/section.html"
        icon = "placeholder"
        label = "Section"


class BlogBodyStreamBlock(blocks.StreamBlock):
    rich_text = blocks.RichTextBlock(features=RICHTEXT_FEATURES)
    image = ImageBlock()
    gallery = GalleryBlock()
    embed = EmbedBlock()
    code = CodeBlock()
    table = TableBlock()
    callout = CalloutBlock()
    button = ButtonBlock()
    divider = DividerBlock()
    spacer = SpacerBlock()
    section = SectionBlock()

    class Meta:
        icon = "doc-full"
        label = "Body"
