from django.shortcuts import get_object_or_404, render
from django.views import generic
from chat.forms import ChatForm

from langchain.chains import RetrievalQA
from langchain.llms import OpenAI


from games.models import Game


class IndexView(generic.ListView):
    template_name = "chats/index.html"
    context_object_name = "games"

    def get_queryset(self):
        """Return the last five published questions."""
        return Game.objects.order_by("-created_at")


def chat_view(request, game_id):
    game = get_object_or_404(Game, pk=game_id)

    question = None
    answer = None
    if request.method == "POST":
        # Process answer
        form = ChatForm(request.POST)
        if form.is_valid():
            question = form.cleaned_data["question"]

            qc_chain = RetrievalQA.from_chain_type(
                llm=OpenAI(),
                chain_type="stuff",
                retriever=game.vector_store.index.as_retriever(),
            )
            answer = qc_chain.run(question)

    return render(
        request,
        "chats/chat.html",
        {"game": game, "question": question, "answer": answer, "form": ChatForm()},
    )
