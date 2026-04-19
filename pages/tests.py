from django.test import TestCase
from django.urls import reverse


class HealthcheckViewTests(TestCase):
    def test_up_view(self):
        response = self.client.get(reverse("up"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"ok")
