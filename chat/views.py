from django.contrib.auth.mixins import LoginRequiredMixin
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
        return Game.objects.filter(ingested=True).order_by("name")


class SessionIndexView(LoginRequiredMixin, generic.ListView):
    login_url = "/users/login"
    redirect_field_name = "next"

    template_name = "chat/sessions.html"
    context_object_name = "chat_sessions"

    def get_queryset(self):
        sessions = ChatSession.objects.filter(user=self.request.user).order_by(
            "-updated_at"
        )
        # re-order based on the last message
        return sorted(
            sessions,
            key=lambda x: x.message_set.last().created_at
            if x.message_set.last()
            else x.updated_at,
            reverse=True,
        )


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

    ip_address = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if not ip_address:
        ip_address = request.META.get("REMOTE_ADDR", "")

    if request.user.is_authenticated:
        chat_session = ChatSession.objects.create(
            game=game, user=request.user, ip_address=ip_address
        )
    else:
        chat_session = ChatSession.objects.create(game=game, ip_address=ip_address)

    return redirect(
        reverse("chat:view_chat_session", args=(chat_session.session_slug,))
    )
