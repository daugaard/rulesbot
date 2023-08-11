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
