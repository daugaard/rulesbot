from django.urls import path

from . import views


app_name = "chat"
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("sessions/", views.SessionIndexView.as_view(), name="sessions"),
    path(
        "create/<int:game_id>/", views.create_chat_session, name="create_chat_session"
    ),
    path("<str:session_slug>", views.view_chat_session, name="view_chat_session"),
]
