from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from games.models import Game


class GamesSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.8

    def items(self):
        return Game.objects.all()

    def location(self, item):
        return reverse("games:detail", args=(item.slug,))
