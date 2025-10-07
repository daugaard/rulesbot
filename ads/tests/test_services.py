from django.test import TestCase

from ads.models import Ad, AdImpression
from ads.services import (
    _weighted_random_choice,
    get_ad_for_game,
    serve_ad_with_impression,
)
from games.models import Game


class AdSelectionServiceTest(TestCase):
    """Tests for ad selection service functions"""

    def setUp(self):
        self.game = Game.objects.create(name="Test Game", ingested=True)

    def test_weighted_random_selection_with_single_ad(self):
        """Test that weighted selection works with a single ad"""
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
        result = _weighted_random_choice([])
        self.assertIsNone(result)

    def test_weighted_random_selection_respects_weights(self):
        """Test that ads with higher weights are selected more often"""
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
        result = get_ad_for_game(self.game)
        self.assertIsNone(result)

    def test_get_ad_for_game_prefers_game_specific_over_generic(self):
        """Test that game-specific ads are prioritized over generic ads"""
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
        result = serve_ad_with_impression(self.game)

        self.assertIsNone(result)
        self.assertEqual(AdImpression.objects.count(), 0)

    def test_weighted_selection_with_multiple_game_specific_ads(self):
        """Test weighted selection among multiple game-specific ads"""
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
