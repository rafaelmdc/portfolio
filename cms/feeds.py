from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Atom1Feed

from .models import BlogPage


class BlogRssFeed(Feed):
    title = "Rafael Correia — Blog"
    link = "/blog/"
    description = "Latest posts on software, research and data science."

    def items(self):
        return (
            BlogPage.objects.live()
            .public()
            .order_by("-first_published_at")[:20]
        )

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.intro or ""

    def item_link(self, item):
        return item.url

    def item_pubdate(self, item):
        return item.first_published_at

    def item_updateddate(self, item):
        return item.last_published_at


class BlogAtomFeed(BlogRssFeed):
    feed_type = Atom1Feed
    subtitle = BlogRssFeed.description
