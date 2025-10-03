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
