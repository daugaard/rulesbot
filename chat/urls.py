from django.urls import path

from . import views


app_name = "chats"
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    # ex: /chats/5/
    path("<int:game_id>/", views.chat_view, name="chat"),
]
