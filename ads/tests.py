from django.test import TestCase

from ads.models import Ad, AdClick, AdImpression
from games.models import Game


class AdModelTest(TestCase):
    def setUp(self):
        self.game = Game.objects.create(name="Test Game", ingested=True)

    def test_create_generic_ad(self):
        """Test creating a generic ad (no game association)"""
        ad = Ad.objects.create(
            title="Generic Ad",
            description="This is a generic ad for all games",
            link="https://example.com/product",
            weight=5,
        )

        self.assertEqual(ad.title, "Generic Ad")
        self.assertIsNone(ad.game)
        self.assertEqual(ad.weight, 5)
        self.assertEqual(str(ad), "Generic Ad (Generic)")

    def test_create_game_specific_ad(self):
        """Test creating a game-specific ad"""
        ad = Ad.objects.create(
            title="Game Specific Ad",
            description="This is a game-specific ad",
            link="https://example.com/game-product",
            game=self.game,
            weight=10,
        )

        self.assertEqual(ad.title, "Game Specific Ad")
        self.assertEqual(ad.game, self.game)
        self.assertEqual(ad.weight, 10)
        self.assertEqual(str(ad), f"Game Specific Ad ({self.game.name})")

    def test_ad_with_image(self):
        """Test creating an ad with an image URL"""
        ad = Ad.objects.create(
            title="Ad with Image",
            description="This ad has an image",
            image="https://example.com/image.jpg",
            link="https://example.com/product",
        )

        self.assertEqual(ad.image, "https://example.com/image.jpg")

    def test_ad_default_weight(self):
        """Test that default weight is 1"""
        ad = Ad.objects.create(
            title="Default Weight Ad",
            description="Testing default weight",
            link="https://example.com/product",
        )

        self.assertEqual(ad.weight, 1)

    def test_impressions_count_zero(self):
        """Test that impressions_count returns 0 when no impressions exist"""
        ad = Ad.objects.create(
            title="Test Ad",
            description="Testing impressions",
            link="https://example.com/product",
        )

        self.assertEqual(ad.impressions_count, 0)

    def test_impressions_count(self):
        """Test that impressions_count returns correct count"""
        ad = Ad.objects.create(
            title="Test Ad",
            description="Testing impressions",
            link="https://example.com/product",
        )

        # Create some impressions
        AdImpression.objects.create(ad=ad)
        AdImpression.objects.create(ad=ad)
        AdImpression.objects.create(ad=ad)

        self.assertEqual(ad.impressions_count, 3)

    def test_clicks_count_zero(self):
        """Test that clicks_count returns 0 when no clicks exist"""
        ad = Ad.objects.create(
            title="Test Ad",
            description="Testing clicks",
            link="https://example.com/product",
        )

        self.assertEqual(ad.clicks_count, 0)

    def test_clicks_count(self):
        """Test that clicks_count returns correct count"""
        ad = Ad.objects.create(
            title="Test Ad",
            description="Testing clicks",
            link="https://example.com/product",
        )

        # Create some clicks
        AdClick.objects.create(ad=ad)
        AdClick.objects.create(ad=ad)

        self.assertEqual(ad.clicks_count, 2)

    def test_ctr_zero_impressions(self):
        """Test that CTR returns 0 when there are no impressions"""
        ad = Ad.objects.create(
            title="Test Ad",
            description="Testing CTR",
            link="https://example.com/product",
        )

        self.assertEqual(ad.ctr, 0)

    def test_ctr_calculation(self):
        """Test CTR calculation"""
        ad = Ad.objects.create(
            title="Test Ad",
            description="Testing CTR",
            link="https://example.com/product",
        )

        # Create 10 impressions and 2 clicks (20% CTR)
        for _ in range(10):
            AdImpression.objects.create(ad=ad)
        for _ in range(2):
            AdClick.objects.create(ad=ad)

        self.assertEqual(ad.ctr, 20.0)

    def test_ctr_perfect_conversion(self):
        """Test CTR when every impression becomes a click"""
        ad = Ad.objects.create(
            title="Test Ad",
            description="Testing CTR",
            link="https://example.com/product",
        )

        # Create 5 impressions and 5 clicks (100% CTR)
        for _ in range(5):
            AdImpression.objects.create(ad=ad)
            AdClick.objects.create(ad=ad)

        self.assertEqual(ad.ctr, 100.0)


class AdImpressionModelTest(TestCase):
    def test_create_impression(self):
        """Test creating an ad impression"""
        ad = Ad.objects.create(
            title="Test Ad",
            description="Testing impression creation",
            link="https://example.com/product",
        )

        impression = AdImpression.objects.create(ad=ad)

        self.assertEqual(impression.ad, ad)
        self.assertIsNotNone(impression.timestamp)
        self.assertTrue(str(impression).startswith(f"Impression: {ad.title}"))

    def test_impression_ordering(self):
        """Test that impressions are ordered by timestamp (newest first)"""
        ad = Ad.objects.create(
            title="Test Ad",
            description="Testing impression ordering",
            link="https://example.com/product",
        )

        impression1 = AdImpression.objects.create(ad=ad)
        impression2 = AdImpression.objects.create(ad=ad)
        impression3 = AdImpression.objects.create(ad=ad)

        impressions = AdImpression.objects.all()
        self.assertEqual(impressions[0], impression3)
        self.assertEqual(impressions[1], impression2)
        self.assertEqual(impressions[2], impression1)


class AdClickModelTest(TestCase):
    def test_create_click(self):
        """Test creating an ad click"""
        ad = Ad.objects.create(
            title="Test Ad",
            description="Testing click creation",
            link="https://example.com/product",
        )

        click = AdClick.objects.create(ad=ad)

        self.assertEqual(click.ad, ad)
        self.assertIsNotNone(click.timestamp)
        self.assertTrue(str(click).startswith(f"Click: {ad.title}"))

    def test_click_ordering(self):
        """Test that clicks are ordered by timestamp (newest first)"""
        ad = Ad.objects.create(
            title="Test Ad",
            description="Testing click ordering",
            link="https://example.com/product",
        )

        click1 = AdClick.objects.create(ad=ad)
        click2 = AdClick.objects.create(ad=ad)
        click3 = AdClick.objects.create(ad=ad)

        clicks = AdClick.objects.all()
        self.assertEqual(clicks[0], click3)
        self.assertEqual(clicks[1], click2)
        self.assertEqual(clicks[2], click1)

    def test_cascade_delete(self):
        """Test that clicks are deleted when ad is deleted"""
        ad = Ad.objects.create(
            title="Test Ad",
            description="Testing cascade delete",
            link="https://example.com/product",
        )

        AdClick.objects.create(ad=ad)
        AdClick.objects.create(ad=ad)

        self.assertEqual(AdClick.objects.count(), 2)

        ad.delete()

        self.assertEqual(AdClick.objects.count(), 0)


class AdSelectionServiceTest(TestCase):
    """Tests for ad selection service functions"""

    def setUp(self):
        self.game = Game.objects.create(name="Test Game", ingested=True)

    def test_weighted_random_selection_with_single_ad(self):
        """Test that weighted selection works with a single ad"""
        from ads.services import _weighted_random_choice

        ad = Ad.objects.create(
            title="Single Ad",
            description="Only one ad",
            link="https://example.com/product",
            weight=5,
        )

        result = _weighted_random_choice([ad])
        self.assertEqual(result, ad)

    def test_weighted_random_selection_with_empty_list(self):
        """Test that weighted selection returns None for empty list"""
        from ads.services import _weighted_random_choice

        result = _weighted_random_choice([])
        self.assertIsNone(result)

    def test_weighted_random_selection_respects_weights(self):
        """Test that ads with higher weights are selected more often"""
        from ads.services import _weighted_random_choice

        # Create ads with very different weights
        low_weight_ad = Ad.objects.create(
            title="Low Weight",
            description="Should be selected less",
            link="https://example.com/low",
            weight=1,
        )
        high_weight_ad = Ad.objects.create(
            title="High Weight",
            description="Should be selected more",
            link="https://example.com/high",
            weight=100,
        )

        ads = [low_weight_ad, high_weight_ad]

        # Run selection 100 times and count results
        selections = {}
        for _ in range(100):
            selected = _weighted_random_choice(ads)
            selections[selected.id] = selections.get(selected.id, 0) + 1

        # High weight ad should be selected significantly more often
        # With weights 1:100, we expect roughly 1:100 ratio
        # Allow some variance but high weight should dominate
        self.assertGreater(
            selections[high_weight_ad.id],
            selections.get(low_weight_ad.id, 0),
            "Higher weighted ad should be selected more often",
        )

    def test_get_ad_for_game_returns_game_specific_ad(self):
        """Test that game-specific ads are returned when available"""
        from ads.services import get_ad_for_game

        # Create a game-specific ad
        game_ad = Ad.objects.create(
            title="Game Specific Ad",
            description="For this game",
            link="https://example.com/game",
            game=self.game,
            weight=1,
        )

        # Create a generic ad
        Ad.objects.create(
            title="Generic Ad",
            description="For all games",
            link="https://example.com/generic",
            weight=1,
        )

        result = get_ad_for_game(self.game)
        self.assertEqual(result, game_ad)

    def test_get_ad_for_game_falls_back_to_generic(self):
        """Test that generic ads are returned when no game-specific ads exist"""
        from ads.services import get_ad_for_game

        # Create only a generic ad
        generic_ad = Ad.objects.create(
            title="Generic Ad",
            description="For all games",
            link="https://example.com/generic",
            weight=1,
        )

        result = get_ad_for_game(self.game)
        self.assertEqual(result, generic_ad)

    def test_get_ad_for_game_returns_none_when_no_ads(self):
        """Test that None is returned when no ads are available"""
        from ads.services import get_ad_for_game

        result = get_ad_for_game(self.game)
        self.assertIsNone(result)

    def test_get_ad_for_game_prefers_game_specific_over_generic(self):
        """Test that game-specific ads are prioritized over generic ads"""
        from ads.services import get_ad_for_game

        # Create game-specific ads for this game
        game_ad = Ad.objects.create(
            title="Game Ad",
            description="For this game",
            link="https://example.com/game",
            game=self.game,
            weight=1,
        )

        # Create generic ads
        Ad.objects.create(
            title="Generic Ad",
            description="For all games",
            link="https://example.com/generic",
            weight=100,  # Higher weight but should not be selected
        )

        # Run multiple times to ensure game-specific is always preferred
        for _ in range(10):
            result = get_ad_for_game(self.game)
            self.assertEqual(
                result,
                game_ad,
                "Game-specific ad should always be selected when available",
            )

    def test_serve_ad_with_impression_logs_impression(self):
        """Test that serving an ad logs an impression"""
        from ads.services import serve_ad_with_impression

        ad = Ad.objects.create(
            title="Test Ad",
            description="Test impression logging",
            link="https://example.com/product",
            game=self.game,
        )

        self.assertEqual(AdImpression.objects.count(), 0)

        result = serve_ad_with_impression(self.game)

        self.assertEqual(result, ad)
        self.assertEqual(AdImpression.objects.count(), 1)
        self.assertEqual(AdImpression.objects.first().ad, ad)

    def test_serve_ad_with_impression_no_ads_available(self):
        """Test that serving an ad returns None and logs no impression when no ads available"""
        from ads.services import serve_ad_with_impression

        result = serve_ad_with_impression(self.game)

        self.assertIsNone(result)
        self.assertEqual(AdImpression.objects.count(), 0)

    def test_weighted_selection_with_multiple_game_specific_ads(self):
        """Test weighted selection among multiple game-specific ads"""
        from ads.services import get_ad_for_game

        # Create multiple game-specific ads with different weights
        ad1 = Ad.objects.create(
            title="Ad 1",
            description="Weight 1",
            link="https://example.com/1",
            game=self.game,
            weight=1,
        )
        ad2 = Ad.objects.create(
            title="Ad 2",
            description="Weight 5",
            link="https://example.com/2",
            game=self.game,
            weight=5,
        )
        ad3 = Ad.objects.create(
            title="Ad 3",
            description="Weight 10",
            link="https://example.com/3",
            game=self.game,
            weight=10,
        )

        # Run selection multiple times and ensure all ads can be selected
        selected_ids = set()
        for _ in range(50):
            result = get_ad_for_game(self.game)
            selected_ids.add(result.id)

        self.assertIn(ad1.id, selected_ids)
        self.assertIn(ad2.id, selected_ids)
        self.assertIn(ad3.id, selected_ids)

    def test_weighted_selection_with_multiple_generic_ads(self):
        """Test weighted selection among multiple generic ads"""
        from ads.services import get_ad_for_game

        # Create multiple generic ads with different weights
        ad1 = Ad.objects.create(
            title="Generic 1",
            description="Weight 1",
            link="https://example.com/1",
            weight=1,
        )
        ad2 = Ad.objects.create(
            title="Generic 2",
            description="Weight 3",
            link="https://example.com/2",
            weight=3,
        )

        # Run selection multiple times and ensure ads can be selected
        selected_ids = set()
        for _ in range(50):
            result = get_ad_for_game(self.game)
            selected_ids.add(result.id)

        # Both ads should be selected at least once in 50 tries
        self.assertIn(ad1.id, selected_ids)
        self.assertIn(ad2.id, selected_ids)


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
        from django.test import RequestFactory

        from ads.views import ad_click_redirect

        factory = RequestFactory()
        request = factory.get(f"/ads/click/{self.ad.id}/")

        response = ad_click_redirect(request, self.ad.id)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.ad.link)
        self.assertEqual(AdClick.objects.count(), 1)
        self.assertEqual(AdClick.objects.first().ad, self.ad)

    def test_ad_click_redirect_invalid_ad(self):
        """Test ad click redirect with an invalid ad ID"""
        from django.test import RequestFactory

        from ads.views import ad_click_redirect

        factory = RequestFactory()
        request = factory.get("/ads/click/9999/")  # Non-existent ad ID

        response = ad_click_redirect(request, 9999)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/")  # Redirects to homepage
        self.assertEqual(AdClick.objects.count(), 0)

    def test_ad_click_redirect_invalid_ad_with_referrer(self):
        """Test ad click redirect with an invalid ad ID and a referrer header"""
        from django.test import RequestFactory

        from ads.views import ad_click_redirect

        factory = RequestFactory()
        request = factory.get("/ads/click/9999/", HTTP_REFERER="/some-page/")

        response = ad_click_redirect(request, 9999)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/some-page/")  # Redirects to referrer
        self.assertEqual(AdClick.objects.count(), 0)
