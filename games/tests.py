import shutil
from unittest import mock

from django.contrib.admin.sites import AdminSite
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import RequestFactory, TestCase
from django.urls import reverse
from langchain.document_loaders import PyPDFLoader

from games.admin import GameAdmin
from games.models import Document, Game
from games.services.document_ingestion_service import ingest_document
from games.vectorstores import GameVectorStore


class GameIndexViewTests(TestCase):
    def test_no_games(self):
        """
        If no games exist, an appropriate message is displayed.
        """
        response = self.client.get(reverse("games:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No games are available.")
        self.assertQuerysetEqual(response.context["games"], [])

    def test_one_game(self):
        """
        If one game exists, it is displayed.
        """
        game = Game.objects.create(name="Test Game")
        response = self.client.get(reverse("games:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Game")
        self.assertQuerysetEqual(response.context["games"], [game])

    def test_many_games(self):
        games = [Game.objects.create(name=f"Test Game {i}") for i in range(10)]
        response = self.client.get(reverse("games:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Game 0")
        self.assertQuerysetEqual(response.context["games"], games)

    # TODO: When we get there make sure non-ingested games are not displayed


class GameDetailViewTests(TestCase):
    def test_no_game(self):
        """
        If no game exists, a 404 is returned.
        """
        response = self.client.get(reverse("games:detail", args=("test",)))
        self.assertEqual(response.status_code, 404)

    def test_one_game(self):
        """
        If one game exists, it is displayed.
        """
        game = Game.objects.create(name="Test Game")
        response = self.client.get(reverse("games:detail", args=(game.slug,)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Game")
        self.assertEqual(response.context["game"], game)

    # TODO: When we get there make sure non-ingested games are not displayed


class DocumentIngestionServiceTest(TestCase):
    def test_ingest_document(self):
        """
        Test that a document is ingested correctly
        """
        game = Game.objects.create(name="Test Game")
        document = Document.objects.create(game=game, url="some-url")

        # Patch / mock document ingestion._download_to_file and replace it with a function that returns a file with the contents of the test.pdf file
        with mock.patch(
            "games.services.document_ingestion_service._download_to_file"
        ) as _download_to_file_mock:
            _download_to_file_mock.side_effect = lambda _, file: shutil.copyfile(
                "games/fixtures/test.pdf", file.name
            )
            ingest_document(document)

        # try to make a similarity search for the document
        results = game.vector_store.index.similarity_search("page 1")

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].metadata["page"], 0)
        self.assertEqual(results[0].metadata["game_id"], game.id)
        self.assertEqual(results[0].metadata["document_id"], document.id)
        self.assertTrue("Page\n1" in results[0].page_content)


class GameVectorStoreTest(TestCase):
    def test_happy_path(self):
        game = Game.objects.create(name="Test Game")

        game_vector_store = GameVectorStore(game)

        docs = PyPDFLoader("games/fixtures/test.pdf").load_and_split()

        game_vector_store.add_documents(docs, 0)

        results = game_vector_store.index.similarity_search("page 1")

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].metadata["page"], 0)
        self.assertEqual(results[0].metadata["game_id"], game.id)
        self.assertEqual(results[0].metadata["document_id"], 0)

    def test_load_from_storage(self):
        game = Game.objects.create(name="Test Game")
        docs = PyPDFLoader("games/fixtures/test.pdf").load_and_split()

        game_vector_store = GameVectorStore(game)
        game_vector_store.add_documents(docs, 0)

        loaded_vector_store = GameVectorStore(game)
        self.assertIsNotNone(loaded_vector_store.index)

        result = loaded_vector_store.index.similarity_search("page 1")

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].metadata["page"], 0)
        self.assertEqual(result[0].metadata["game_id"], game.id)
        self.assertEqual(result[0].metadata["document_id"], 0)


class GameAdminTest(TestCase):
    def get_ingest_documents_request(self):
        request = RequestFactory().get("/admin/games/game")
        setattr(request, "session", "session")
        messages = FallbackStorage(request)
        setattr(request, "_messages", messages)
        return request

    def test_ingest_documents(self):
        game = Game.objects.create(name="Test Game")
        document = Document.objects.create(game=game, url="some-url")

        # Patch / mock document ingestion._download_to_file and replace it with a function that returns a file with the contents of the test.pdf file
        with mock.patch(
            "games.services.document_ingestion_service._download_to_file"
        ) as _download_to_file_mock:
            _download_to_file_mock.side_effect = lambda _, file: shutil.copyfile(
                "games/fixtures/test.pdf", file.name
            )
            GameAdmin(Game, AdminSite()).ingest_documents(
                self.get_ingest_documents_request(), [game]
            )

        game.refresh_from_db()

        # try to make a similarity search for the document
        results = game.vector_store.index.similarity_search("page 1")

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].metadata["page"], 0)
        self.assertEqual(results[0].metadata["game_id"], game.id)
        self.assertEqual(results[0].metadata["document_id"], document.id)
        self.assertTrue("Page\n1" in results[0].page_content)

    def test_ingest_documents_twice(self):
        game = Game.objects.create(name="Test Game")
        document = Document.objects.create(game=game, url="some-url")

        # Patch / mock document ingestion._download_to_file and replace it with a function that returns a file with the contents of the test.pdf file
        with mock.patch(
            "games.services.document_ingestion_service._download_to_file"
        ) as _download_to_file_mock:
            _download_to_file_mock.side_effect = lambda _, file: shutil.copyfile(
                "games/fixtures/test.pdf", file.name
            )
            GameAdmin(Game, AdminSite()).ingest_documents(
                self.get_ingest_documents_request(), [game]
            )

            # Call it a second time
            GameAdmin(Game, AdminSite()).ingest_documents(
                self.get_ingest_documents_request(), [game]
            )

        game.refresh_from_db()

        # try to make a similarity search for the document
        results = game.vector_store.index.similarity_search("page 1")

        self.assertEqual(len(results), 2)  # Still should only show 2 results
        self.assertEqual(results[0].metadata["page"], 0)
        self.assertEqual(results[0].metadata["game_id"], game.id)
        self.assertEqual(results[0].metadata["document_id"], document.id)
        self.assertTrue("Page\n1" in results[0].page_content)


class GameModelTest(TestCase):
    def test_game_str(self):
        game = Game.objects.create(name="Test Game")
        self.assertEqual(str(game), "Test Game")

    def test_game_with_docs(self):
        game = Game.objects.create(name="Test Game")
        Document.objects.create(game=game, url="some-url")
        Document.objects.create(
            game=game, url="some--other-url", display_name="some-different-url"
        )
