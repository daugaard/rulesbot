from django.urls import path

from . import views

app_name = "games"
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    # ex: /games/rules/name-slug/
    path("rules/<slug:slug>/", views.DetailView.as_view(), name="detail"),
]
