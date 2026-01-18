from django import template
from bs4 import BeautifulSoup

register = template.Library()

@register.filter(is_safe=True)
def bootstrapify(html):
    """
    Enhance CKEditor HTML for Bootstrap:
      - images → responsive & centered
      - tables → styled
      - headings → centered
      - paragraphs → justified
      - iframes → responsive (16x9)
    """
    if not html:
        return ""

    soup = BeautifulSoup(html, "html.parser")

    # ---------- IMAGES ----------
    for img in soup.find_all("img"):
        # ensure responsive scaling
        img_classes = set(img.get("class", []))
        img_classes.update(["img-fluid", "rounded"])
        img["class"] = list(img_classes)
        # wrap image in centered figure if not already
        if img.parent.name != "figure":
            figure = soup.new_tag("figure", **{"class": "text-center my-4"})
            img.wrap(figure)

    # ---------- TABLES ----------
    for table in soup.find_all("table"):
        table_classes = set(table.get("class", []))
        table_classes.update(["table", "table-striped", "table-bordered", "table-sm"])
        table["class"] = list(table_classes)

    # ---------- HEADINGS ----------
    for header in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]):
        header_classes = set(header.get("class", []))
        header_classes.update(["text-center", "fw-bold", "my-4"])
        header["class"] = list(header_classes)

    # ---------- PARAGRAPHS ----------
    for p in soup.find_all("p"):
        p_classes = set(p.get("class", []))
        p_classes.update(["text-justify", "mb-3"])
        p["class"] = list(p_classes)

    # ---------- IFRAME / VIDEO EMBEDS ----------
    for iframe in soup.find_all("iframe"):
        wrapper = soup.new_tag("div", **{"class": "ratio ratio-16x9 mb-3"})
        iframe.wrap(wrapper)

    return str(soup)
