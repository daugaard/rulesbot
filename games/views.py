from django.shortcuts import get_object_or_404, render
from django.views import generic

from games.models import Game


class IndexView(generic.ListView):
    template_name = "games/index.html"
    context_object_name = "games"

    def get_queryset(self):
        return Game.objects.filter(ingested=True).order_by("name")


def detail_view(request, slug):
    game = get_object_or_404(Game, slug=slug)

    games = Game.objects.filter(ingested=True).order_by("-created_at")[:5]

    return render(request, "games/detail.html", {"game": game, "games": games})
