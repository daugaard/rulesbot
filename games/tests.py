from django.test import TestCase
from django.urls import reverse

from games.models import Document, Game
from games.services import document_ingestion_service

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
        # reverse order because we sort by created_at
        games.reverse()
        self.assertQuerysetEqual(response.context["games"], games)

    ## TODO: When we get there make sure non-ingested games are not displayed

class GameDetailViewTests(TestCase):
    def test_no_game(self):
        """
        If no game exists, a 404 is returned.
        """
        response = self.client.get(reverse("games:detail", args=(1,)))
        self.assertEqual(response.status_code, 404)

    def test_one_game(self):
        """
        If one game exists, it is displayed.
        """
        game = Game.objects.create(name="Test Game")
        response = self.client.get(reverse("games:detail", args=(game.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Game")
        self.assertEqual(response.context["game"], game)

    ## TODO: When we get there make sure non-ingested games are not displayed


class DocumentIngestionServiceTest(TestCase):

    def test_ingest_document(self):
        """
        Test that a document is ingested correctly
        """
        game = Game.objects.create(name="Test Game")
        document = Document.objects.create(game=game, url="https://instructions.hasbro.com/api/download/00390_en-us_sorry-game.pdf")
        document_ingestion_service.ingest_document(document)

        # try to make a similarity search for the document
        