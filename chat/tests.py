from django.test import TestCase
from django.urls import reverse

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
        self.assertEqual(response.url, f"/chats/{game.chat_session.session_slug}")
