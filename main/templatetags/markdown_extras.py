from django import template
import markdown2, bleach

register = template.Library()


@register.filter
def markdownify(text):
    if not text:
        return ""
    html = markdown2.markdown(text)
    clean = bleach.clean(
        html,
        tags=["p", "em", "strong", "a", "ul", "ol", "li", "br"],
        attributes={"a": ["href", "title", "target"]},
    )
    return clean
