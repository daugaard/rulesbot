from unittest import mock

from django.test import TestCase
from django.urls import reverse
from langchain.document_loaders.base import Document
from langchain.embeddings.fake import DeterministicFakeEmbedding
from langchain.schema.messages import AIMessage, HumanMessage
from langchain.vectorstores import FAISS

from chat.models import ChatSession
from chat.retrievers.rules_bot_retriever import RulesBotRetriever
from chat.services.question_answering_service import _get_chat_history, ask_question
from games.models import Game


class CreateChatSessionViewTests(TestCase):
    def test_no_game(self):
        """
        If no game exists, a 404 is returned.
        """
        response = self.client.get(reverse("chat:create_chat_session", args=(1,)))
        self.assertEqual(response.status_code, 404)

    def test_one_game(self):
        """
        If one game exists, it is displayed.
        """
        game = Game.objects.create(name="Test Game")
        response = self.client.get(reverse("chat:create_chat_session", args=(game.id,)))
        self.assertEqual(response.status_code, 302)
        chat_session = game.chatsession_set.first()
        self.assertEqual(response.url, f"/chat/{chat_session.session_slug}")


class QuestionAnsweringServiceTests(TestCase):
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

        max_messages = 8
        self.assertEqual(len(history), max_messages)  # max 8 messages

        self.assertEqual(history[0].content, "Message 16")
        assert isinstance(history[0], HumanMessage)
        self.assertEqual(history[1].content, "Message 16")
        assert isinstance(history[1], AIMessage)
        self.assertEqual(history[2].content, "Message 17")
        assert isinstance(history[2], HumanMessage)
        self.assertEqual(history[3].content, "Message 17")
        assert isinstance(history[3], AIMessage)
        self.assertEqual(history[4].content, "Message 18")
        assert isinstance(history[4], HumanMessage)
        self.assertEqual(history[5].content, "Message 18")
        assert isinstance(history[5], AIMessage)
        self.assertEqual(history[6].content, "Message 19")
        assert isinstance(history[6], HumanMessage)
        self.assertEqual(history[7].content, "Message 19")
        assert isinstance(history[7], AIMessage)

    def test_ask_question(self):
        game = Game.objects.create(name="Test Game")
        document = game.document_set.create(display_name="Rulebook", url="some-url")
        chat_session = ChatSession.objects.create(game=game)

        question = "What is the meaning of life?"

        # Mock _setup_conversational_retrieval_chain
        with mock.patch(
            "chat.services.question_answering_service._setup_conversational_retrieval_chain"
        ) as mock_from_llm:
            mock_from_llm.return_value = mock.MagicMock(
                return_value={
                    "answer": "42",
                    "source_documents": [
                        Document(
                            page_content="some content",
                            metadata={"document_id": document.id, "page": 42},
                        )
                    ],
                }
            )
            ask_question(question, chat_session)

        # Assert that messages are created
        self.assertEqual(chat_session.message_set.count(), 2)
        self.assertEqual(chat_session.message_set.first().message, question)
        self.assertEqual(chat_session.message_set.first().message_type, "human")
        self.assertEqual(chat_session.message_set.last().message, "42")
        self.assertEqual(chat_session.message_set.last().message_type, "ai")
        ai_message = chat_session.message_set.last()
        self.assertEqual(len(ai_message.sourcedocument_set.all()), 1)
        self.assertEqual(ai_message.sourcedocument_set.first().document, document)
        self.assertEqual(
            ai_message.sourcedocument_set.first().page_number, 43
        )  # 0-indexed


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
