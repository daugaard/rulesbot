from django.views import generic

from games.models import Game


class IndexView(generic.ListView):
    template_name = "games/index.html"
    context_object_name = "games"

    def get_queryset(self):
        return Game.objects.order_by("name")


class DetailView(generic.DetailView):
    model = Game
    template_name = "games/detail.html"
