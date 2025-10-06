from queue import SimpleQueue
from threading import Thread

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import StreamingHttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import generic

from ads.services import serve_ad_with_impression
from chat.forms import ChatForm
from chat.models import ChatSession
from chat.services import streaming_question_answering_service
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

    # check if we have permissions to view this session
    if chat_session.user is not None and not request.user == chat_session.user:
        return redirect(reverse("chat:index"))

    # Load the last 7 chat sessions for the user
    sessions = []
    if request.user.is_authenticated:
        sessions = ChatSession.objects.filter(user=request.user)
        sessions = sorted(
            sessions,
            key=lambda x: x.message_set.last().created_at
            if x.message_set.last()
            else x.updated_at,
            reverse=True,
        )

    # Get an ad for this game and log the impression
    ad = serve_ad_with_impression(chat_session.game)

    return render(
        request,
        "chat/chat.html",
        {
            "chat_session": chat_session,
            "form": ChatForm(),
            "sessions": sessions[:7],
            "ad": ad,
        },
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


def ask_question_streaming(request, session_slug):
    """
    Ask a question using the async_ask_question function and return the raw response
    as a streaming response.
    """
    chat_session = get_object_or_404(ChatSession, session_slug=session_slug)

    # check if we have permissions to view this session
    if chat_session.user is not None and not request.user == chat_session.user:
        return redirect(reverse("chat:index"))

    # Question is in X-Chat-Question header
    question = request.META.get("HTTP_X_CHAT_QUESTION", "")

    response_queue = SimpleQueue()

    def stream_from_queue():
        while True:
            result = response_queue.get()
            if (
                result is streaming_question_answering_service.QueueSignals.job_done
                or result is streaming_question_answering_service.QueueSignals.error
            ):
                break
            yield result

    # run the async ask question function in a thread
    qa_thread = Thread(
        target=streaming_question_answering_service.ask_question,
        args=(question, chat_session, response_queue),
    )
    qa_thread.start()

    return StreamingHttpResponse(stream_from_queue())
