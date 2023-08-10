from django.urls import path

from . import views


app_name = "games"
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    # ex: /games/5/
    path("<int:pk>/", views.DetailView.as_view(), name="detail"),
    # ex: /games/5/ingest/
    path("<int:game_id>/ingest/", views.ingest, name="ingest"),
]
