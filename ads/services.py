"""
Ad serving service with weighted random selection.
"""

import random
from typing import Optional

from ads.models import Ad, AdClick, AdImpression
from games.models import Game


def get_ad_for_game(game: Game) -> Optional[Ad]:
    """
    Get an ad for a specific game using weighted random selection.

    First tries to find game-specific ads. If none exist, falls back to generic ads.

    Args:
        game: The game to get an ad for

    Returns:
        An Ad instance, or None if no ads are available
    """
    # Try to get game-specific ads first
    game_ads = list(Ad.objects.filter(game=game))

    if game_ads:
        return _weighted_random_choice(game_ads)

    # Fallback to generic ads
    generic_ads = list(Ad.objects.filter(game__isnull=True))

    if generic_ads:
        return _weighted_random_choice(generic_ads)

    return None


def _weighted_random_choice(ads: list[Ad]) -> Optional[Ad]:
    """
    Select a random ad from the list using weighted random selection.

    Args:
        ads: List of Ad objects to choose from

    Returns:
        A randomly selected Ad based on weights, or None if list is empty
    """
    if not ads:
        return None

    # Get weights for all ads
    weights = [ad.weight for ad in ads]

    # Use random.choices for weighted random selection
    selected = random.choices(ads, weights=weights, k=1)

    return selected[0]


def serve_ad_with_impression(game: Game) -> Optional[Ad]:
    """
    Get an ad for a game and log an impression.

    Args:
        game: The game to get an ad for

    Returns:
        An Ad instance with impression logged, or None if no ads available
    """
    ad = get_ad_for_game(game)

    if ad:
        # Log the impression
        AdImpression.objects.create(ad=ad)

    return ad


def record_ad_click(ad: Ad):
    """
    Record a click for the given ad.

    Args:
        ad: The Ad instance that was clicked
    """
    click = AdClick.objects.create(ad=ad)
    return click
