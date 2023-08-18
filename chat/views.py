from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import generic

from chat.forms import ChatForm
from chat.models import ChatSession
from chat.services import question_answering_service
from games.models import Game


class IndexView(generic.ListView):
    template_name = "chat/index.html"
    context_object_name = "games"

    def get_queryset(self):
        return Game.objects.order_by("-created_at")


class SessionIndexView(generic.ListView):
    template_name = "chat/sessions.html"
    context_object_name = "chat_sessions"

    def get_queryset(self):
        return ChatSession.objects.order_by("-created_at")


class LandingView(generic.ListView):
    template_name = "chat/landing.html"
    context_object_name = "games"

    def get_queryset(self):
        return Game.objects.order_by("-created_at")[:8]


def view_chat_session(request, session_slug):
    chat_session = get_object_or_404(ChatSession, session_slug=session_slug)

    if request.method == "POST":
        # Process answer
        form = ChatForm(request.POST)
        if form.is_valid():
            question = form.cleaned_data["question"]
            question_answering_service.ask_question(question, chat_session)

    return render(
        request,
        "chat/chat.html",
        {"chat_session": chat_session, "form": ChatForm()},
    )


def create_chat_session(request, game_id):
    game = get_object_or_404(Game, pk=game_id)

    chat_session = ChatSession.objects.create(game=game)

    return redirect(
        reverse("chat:view_chat_session", args=(chat_session.session_slug,))
    )
