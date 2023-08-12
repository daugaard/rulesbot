from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import generic
from chat.forms import ChatForm

from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from chat.models import ChatSession


from games.models import Game


class IndexView(generic.ListView):
    template_name = "chats/index.html"
    context_object_name = "games"

    def get_queryset(self):
        return Game.objects.order_by("-created_at")


class SessionIndexView(generic.ListView):
    template_name = "chats/sessions.html"
    context_object_name = "chat_sessions"

    def get_queryset(self):
        return ChatSession.objects.order_by("-created")


def view_chat_session(request, session_slug):
    chat_session = get_object_or_404(ChatSession, session_slug=session_slug)

    question = None
    answer = None
    if request.method == "POST":
        # Process answer
        form = ChatForm(request.POST)
        if form.is_valid():
            question = form.cleaned_data["question"]
            chat_session.message_set.create(message=question, message_type="human")

            qc_chain = RetrievalQA.from_chain_type(
                llm=ChatOpenAI(),
                chain_type="stuff",
                retriever=chat_session.game.vector_store.index.as_retriever(),
            )
            answer = qc_chain.run(question)
            chat_session.message_set.create(message=answer, message_type="ai")

    return render(
        request,
        "chats/chat.html",
        {"chat_session": chat_session, "form": ChatForm()},
    )


def create_chat_session(request, game_id):
    game = get_object_or_404(Game, pk=game_id)

    chat_session = ChatSession.objects.create(game=game)

    return redirect(
        reverse("chats:view_chat_session", args=(chat_session.session_slug,))
    )
