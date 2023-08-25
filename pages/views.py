from django.shortcuts import render
from django.views import generic

from games.models import Game


class LandingView(generic.ListView):
    template_name = "pages/landing.html"
    context_object_name = "games"

    def get_queryset(self):
        return Game.objects.order_by("-created_at")[:5]


def AboutView(request):
    return render(request, "pages/about.html")


def TermsView(request):
    return render(request, "pages/terms.html")
