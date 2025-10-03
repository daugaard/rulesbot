from django.db import models

from games.models import Game


class Ad(models.Model):
    """
    Advertisement model that can be either game-specific or generic.
    Uses weighted random selection for serving.
    """

    title = models.CharField(max_length=255)
    description = models.TextField(max_length=500)
    image = models.URLField(blank=True, null=True, help_text="Optional image URL")
    link = models.URLField(help_text="Target URL (e.g., Amazon affiliate link)")
    game = models.ForeignKey(
        Game,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Leave blank for generic ads shown on all games",
    )
    weight = models.PositiveIntegerField(
        default=1, help_text="Higher weight = more likely to be shown"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        game_info = f" ({self.game.name})" if self.game else " (Generic)"
        return f"{self.title}{game_info}"

    @property
    def impressions_count(self):
        return self.adimpression_set.count()

    @property
    def clicks_count(self):
        return self.adclick_set.count()

    @property
    def ctr(self):
        """Click-through rate as a percentage"""
        if self.impressions_count == 0:
            return 0
        return (self.clicks_count / self.impressions_count) * 100


class AdImpression(models.Model):
    """
    Tracks each time an ad is displayed to a user.
    """

    ad = models.ForeignKey(Ad, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["ad", "-timestamp"]),
        ]

    def __str__(self):
        return f"Impression: {self.ad.title} at {self.timestamp}"


class AdClick(models.Model):
    """
    Tracks each time a user clicks on an ad.
    """

    ad = models.ForeignKey(Ad, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["ad", "-timestamp"]),
        ]

    def __str__(self):
        return f"Click: {self.ad.title} at {self.timestamp}"
