from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic

from games.models import Game


class IndexView(generic.ListView):
    template_name = "games/index.html"
    context_object_name = "games"

    def get_queryset(self):
        """Return the last five published questions."""
        return Game.objects.order_by("-created_at")

class DetailView(generic.DetailView):
    model = Game
    template_name = "games/detail.html"


def ingest(request, game_id):
    game = get_object_or_404(Game, pk=game_id)
    game.ingested = True
    game.save()

    return HttpResponseRedirect(reverse("games:detail", args=(game_id,)))