from django.contrib.sitemaps import Sitemap

from blog.models import Post


class PostSitemap(Sitemap):
    # changefreq and priority can also be methods
    changefreq = "weekly"
    priority = 0.9

    def items(self):
        # By default, Django calls get_absolute_url() on each returned object.
        # We can implement location() if we want to change that.
        return Post.published.all()

    def lastmod(self, obj):
        # Receive each object returned by items()
        return obj.updated
