from django.test import RequestFactory, TestCase

from ads.models import Ad, AdClick
from ads.views import ad_click_redirect
from games.models import Game


class AdClickViewTest(TestCase):
    def setUp(self):
        self.game = Game.objects.create(name="Test Game", ingested=True)
        self.ad = Ad.objects.create(
            title="Test Ad",
            description="Testing ad click view",
            link="https://example.com/product",
            game=self.game,
        )

    def test_ad_click_redirect_valid_ad(self):
        """Test ad click redirect with a valid ad ID"""
        factory = RequestFactory()
        request = factory.get(f"/ads/click/{self.ad.id}/")

        response = ad_click_redirect(request, self.ad.id)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.ad.link)
        self.assertEqual(AdClick.objects.count(), 1)
        self.assertEqual(AdClick.objects.first().ad, self.ad)

    def test_ad_click_redirect_invalid_ad(self):
        """Test ad click redirect with an invalid ad ID"""
        factory = RequestFactory()
        request = factory.get("/ads/click/9999/")  # Non-existent ad ID

        response = ad_click_redirect(request, 9999)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/")  # Redirects to homepage
        self.assertEqual(AdClick.objects.count(), 0)

    def test_ad_click_redirect_invalid_ad_with_referrer(self):
        """Test ad click redirect with an invalid ad ID and a referrer header"""
        factory = RequestFactory()
        request = factory.get("/ads/click/9999/", HTTP_REFERER="/some-page/")

        response = ad_click_redirect(request, 9999)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/some-page/")  # Redirects to referrer
        self.assertEqual(AdClick.objects.count(), 0)
