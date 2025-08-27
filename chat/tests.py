from multiprocessing import SimpleQueue
from unittest import mock

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from langchain.schema.messages import AIMessage, HumanMessage
from langchain_community.embeddings.fake import DeterministicFakeEmbedding
from langchain_community.llms.fake import FakeListLLM, FakeStreamingListLLM
from langchain_community.vectorstores import FAISS
from langchain_core.documents.base import Document

from chat.models import ChatSession
from chat.retrievers.rules_bot_retriever import RulesBotRetriever
from chat.services.streaming_question_answering_service import (
    QueueSignals,
    _get_chat_history,
    ask_question,
)
from games.models import Game
from tests.decorators import prevent_request_warnings, prevent_warnings


class CreateChatSessionViewTests(TestCase):
    @prevent_request_warnings
    def test_no_game(self):
        """
        If no game exists, a 404 is returned.
        """
        response = self.client.get(reverse("chat:create_chat_session", args=(1,)))
        self.assertEqual(response.status_code, 404)

    def test_one_game(self):
        game = Game.objects.create(name="Test Game")
        response = self.client.get(reverse("chat:create_chat_session", args=(game.id,)))
        self.assertEqual(response.status_code, 302)
        chat_session = game.chatsession_set.first()
        self.assertEqual(response.url, f"/chat/{chat_session.session_slug}")
        self.assertIsNone(chat_session.user)  # No user associated with session

    def test_user_logged_in(self):
        user = User.objects.create_user(username="testuser", password="12345")
        self.client.login(username="testuser", password="12345")
        game = Game.objects.create(name="Test Game")
        response = self.client.get(reverse("chat:create_chat_session", args=(game.id,)))
        self.assertEqual(response.status_code, 302)
        chat_session = game.chatsession_set.first()
        self.assertEqual(response.url, f"/chat/{chat_session.session_slug}")
        self.assertEqual(chat_session.user, user)  # User associated with session


class StreamingQuestionAnsweringServiceTests(TestCase):
    def test__get_chat_history_empty(self):
        game = Game.objects.create(name="Test Game")
        chat_session = ChatSession.objects.create(game=game)

        history = _get_chat_history(chat_session)

        self.assertEqual(history, [])

    def test__get_chat_history_few_messages(self):
        game = Game.objects.create(name="Test Game")
        chat_session = ChatSession.objects.create(game=game)

        chat_session.message_set.create(message="Hello", message_type="human")
        chat_session.message_set.create(message="Hi", message_type="ai")

        history = _get_chat_history(chat_session)

        self.assertEqual(len(history), 2)
        self.assertEqual(history[0].content, "Hello")
        assert isinstance(history[0], HumanMessage)
        self.assertEqual(history[1].content, "Hi")
        assert isinstance(history[1], AIMessage)

    def test__get_chat_histry_many_messages(self):
        game = Game.objects.create(name="Test Game")
        chat_session = ChatSession.objects.create(game=game)

        for i in range(20):
            chat_session.message_set.create(
                message=f"Message {i}", message_type="human"
            )
            chat_session.message_set.create(message=f"Message {i}", message_type="ai")

        history = _get_chat_history(chat_session)

        max_messages = 12
        self.assertEqual(len(history), max_messages)  # max 12 messages

        self.assertEqual(history[0].content, "Message 14")
        assert isinstance(history[0], HumanMessage)
        self.assertEqual(history[1].content, "Message 14")
        assert isinstance(history[1], AIMessage)
        self.assertEqual(history[2].content, "Message 15")
        assert isinstance(history[2], HumanMessage)
        self.assertEqual(history[3].content, "Message 15")
        assert isinstance(history[3], AIMessage)
        self.assertEqual(history[4].content, "Message 16")
        assert isinstance(history[4], HumanMessage)
        self.assertEqual(history[5].content, "Message 16")
        assert isinstance(history[5], AIMessage)
        self.assertEqual(history[6].content, "Message 17")
        assert isinstance(history[6], HumanMessage)
        self.assertEqual(history[7].content, "Message 17")
        assert isinstance(history[7], AIMessage)
        self.assertEqual(history[8].content, "Message 18")
        assert isinstance(history[8], HumanMessage)
        self.assertEqual(history[9].content, "Message 18")
        assert isinstance(history[9], AIMessage)
        self.assertEqual(history[10].content, "Message 19")
        assert isinstance(history[10], HumanMessage)
        self.assertEqual(history[11].content, "Message 19")
        assert isinstance(history[11], AIMessage)

    @prevent_warnings
    def test_ask_question(self):
        game = Game.objects.create(name="Test Game")
        document = game.document_set.create(display_name="Rulebook", url="some-url")
        chat_session = ChatSession.objects.create(game=game)
        # setup mock index
        chat_session.game.vector_store.add_documents(
            [Document(page_content="some content", metadata={"page": 42})],
            document_id=document.id,
        )
        test_queue = SimpleQueue()

        question = "What is the meaning of life?"

        # Mock the llm
        with mock.patch(
            "chat.services.streaming_question_answering_service.ChatOpenAI"
        ) as mock_llm_initializer:

            def side_effect(*args, **kwargs):
                if kwargs.get("streaming"):
                    return FakeStreamingListLLM(
                        responses=["some answer to the question"], *args, **kwargs
                    )
                else:
                    return FakeListLLM(
                        responses=["some answer to the question"], *args, **kwargs
                    )

            mock_llm_initializer.side_effect = side_effect
            ask_question(question, chat_session, test_queue)

        # Assert that messages are created
        self.assertEqual(chat_session.message_set.count(), 2)
        self.assertEqual(chat_session.message_set.first().message, question)
        self.assertEqual(chat_session.message_set.first().message_type, "human")
        self.assertEqual(
            chat_session.message_set.last().message, "some answer to the question"
        )
        self.assertEqual(chat_session.message_set.last().message_type, "ai")
        ai_message = chat_session.message_set.last()
        self.assertEqual(len(ai_message.sourcedocument_set.all()), 1)
        self.assertEqual(ai_message.sourcedocument_set.first().document, document)
        self.assertEqual(
            ai_message.sourcedocument_set.first().page_number, 43
        )  # 0-indexed

        # Assert that the queue has been filled
        # TODO: For some reason the message isn't posted to the queue when using the FakeStreamingListLLM
        # self.assertEqual(test_queue.get(), "some answer to the question")
        self.assertEqual(test_queue.get(), QueueSignals.job_done)


class RulesBotRetrieverTests(TestCase):
    def documents_for_test_without_setup_page(self):
        return [
            Document(
                page_content="Chess game instructions",
                metadata={"document_id": 1, "page": 42},
            ),
            Document(
                page_content="Checkers game instructions",
                metadata={"document_id": 1, "page": 43},
            ),
            Document(
                page_content="Clue game instructions",
                metadata={"document_id": 1, "page": 44},
            ),
            Document(
                page_content="Monopoly game instructions",
                metadata={"document_id": 1, "page": 45},
            ),
        ]

    def documents_for_test_with_setup_page(self):
        return self.documents_for_test_without_setup_page() + [
            Document(
                page_content="Setup instructions for a game",
                metadata={"document_id": 1, "page": 42, "setup_page": True},
            ),
        ]

    @prevent_warnings
    def test_happy_path(self):
        # Initialze FAISS index
        index = FAISS.from_documents(
            documents=self.documents_for_test_without_setup_page(),
            embedding=DeterministicFakeEmbedding(size=1536),
        )

        docs = RulesBotRetriever(
            index=index, search_kwargs={"k": 3}
        ).get_relevant_documents("clue")

        self.assertEqual(len(docs), 3)
        self.assertEqual(docs[0].metadata["page"], 44)

    @prevent_warnings
    def test_setup_question_special_case(self):
        # Initialze FAISS index
        index = FAISS.from_documents(
            documents=self.documents_for_test_with_setup_page(),
            embedding=DeterministicFakeEmbedding(size=1536),
        )

        docs = RulesBotRetriever(
            index=index, search_kwargs={"k": 3}
        ).get_relevant_documents("how many pieces do you start with?")

        self.assertEqual(len(docs), 3)  # Still only returns 3 results
        self.assertEqual(
            [doc.metadata.get("setup_page") for doc in docs], [None, None, True]
        )

    @prevent_warnings
    def test_setup_question_no_special_case(self):
        index = FAISS.from_documents(
            documents=self.documents_for_test_with_setup_page(),
            embedding=DeterministicFakeEmbedding(size=1536),
        )

        docs = RulesBotRetriever(
            index=index, search_kwargs={"k": 3}
        ).get_relevant_documents("instructions")

        self.assertEqual(len(docs), 3)
        self.assertEqual(
            [doc.metadata.get("setup_page") for doc in docs],
            [
                None,
                None,
                True,
            ],  # Can still include setup page even if it doesn't hit our special case
        )

    @prevent_warnings
    def test_setup_question_special_case_no_setup_page(self):
        # Initialze FAISS index
        index = FAISS.from_documents(
            documents=self.documents_for_test_without_setup_page(),
            embedding=DeterministicFakeEmbedding(size=1536),
        )

        docs = RulesBotRetriever(
            index=index, search_kwargs={"k": 3}
        ).get_relevant_documents("how many pieces do you start with?")

        self.assertEqual(len(docs), 3)  # Return 3 results
        # None are a setup page because there are no setup pages
        self.assertEqual(
            [doc.metadata.get("setup_page") for doc in docs], [None, None, None]
        )
