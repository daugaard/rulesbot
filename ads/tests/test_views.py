from django.test import Client, RequestFactory, TestCase

from ads.models import Ad, AdClick, AdImpression
from ads.views import ad_click_redirect
from chat.models import ChatSession
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


class AdDisplayIntegrationTest(TestCase):
    """Integration tests for ad display on chat pages"""

    def setUp(self):
        self.client = Client()
        self.game = Game.objects.create(name="Catan", ingested=True)
        self.chat_session = ChatSession.objects.create(game=self.game)

    def test_game_specific_ad_displayed_on_chat_page(self):
        """Test that a game-specific ad is displayed on the chat page"""
        ad = Ad.objects.create(
            title="Catan Expansions",
            description="Get the best expansions for Catan!",
            link="https://example.com/catan",
            game=self.game,
            weight=10,
        )

        response = self.client.get(f"/chat/{self.chat_session.session_slug}")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Catan Expansions")
        self.assertContains(response, "Get the best expansions for Catan!")
        self.assertContains(response, f"/ads/click/{ad.id}/")
        # Verify impression was logged
        self.assertEqual(AdImpression.objects.count(), 1)
        self.assertEqual(AdImpression.objects.first().ad, ad)

    def test_generic_ad_displayed_when_no_game_specific_ad(self):
        """Test that a generic ad is displayed when no game-specific ad exists"""
        generic_ad = Ad.objects.create(
            title="Board Game Storage",
            description="Organize your games with our premium storage!",
            link="https://example.com/storage",
            game=None,  # Generic ad
            weight=5,
        )

        response = self.client.get(f"/chat/{self.chat_session.session_slug}")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Board Game Storage")
        self.assertContains(response, "Organize your games with our premium storage!")
        self.assertContains(response, f"/ads/click/{generic_ad.id}/")
        # Verify impression was logged
        self.assertEqual(AdImpression.objects.count(), 1)
        self.assertEqual(AdImpression.objects.first().ad, generic_ad)

    def test_no_ad_displayed_when_no_ads_exist(self):
        """Test that no ad is displayed when no ads exist"""
        response = self.client.get(f"/chat/{self.chat_session.session_slug}")

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'href="/ads/click/')
        # Verify no impression was logged
        self.assertEqual(AdImpression.objects.count(), 0)

    def test_ad_with_image_displayed_correctly(self):
        """Test that an ad with an image is displayed with the image"""
        from django.core.files.uploadedfile import SimpleUploadedFile

        # Create a simple test image
        image_content = (
            b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04"
            b"\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02"
            b"\x02\x4c\x01\x00\x3b"
        )
        test_image = SimpleUploadedFile(
            "test_ad.gif", image_content, content_type="image/gif"
        )

        ad = Ad.objects.create(
            title="Premium Dice Set",
            description="Upgrade your gaming experience!",
            link="https://example.com/dice",
            game=self.game,
            image=test_image,
            weight=8,
        )

        response = self.client.get(f"/chat/{self.chat_session.session_slug}")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Premium Dice Set")
        # Check that the image filename is in the response (URL may have query params)
        self.assertContains(response, "test_ad.gif")
        self.assertContains(response, f"/ads/click/{ad.id}/")

    def test_ad_click_link_opens_in_new_tab(self):
        """Test that ad click links have target='_blank' and rel='noopener'"""
        Ad.objects.create(
            title="Test Ad",
            description="Test Description",
            link="https://example.com/test",
            game=self.game,
        )

        response = self.client.get(f"/chat/{self.chat_session.session_slug}")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'target="_blank"')
        self.assertContains(response, 'rel="noopener"')
