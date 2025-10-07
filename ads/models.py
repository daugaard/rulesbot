from django.db import models

from games.models import Game


class Ad(models.Model):
    """
    Advertisement model that can be either game-specific or generic.
    Uses weighted random selection for serving.
    """

    title = models.CharField(max_length=255)
    description = models.TextField(max_length=500)
    image = models.FileField(
        upload_to="ads/images", null=True, blank=True, help_text="Optional image URL"
    )
    link = models.URLField(
        help_text="Target URL (e.g., Amazon affiliate link)", null=False, blank=False
    )
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

    def get_impressions_count(self, start_date=None, end_date=None):
        """
        Get impression count with optional date filtering.

        Args:
            start_date: Start date for filtering (inclusive)
            end_date: End date for filtering (inclusive)

        Returns:
            Count of impressions within the date range
        """
        queryset = self.adimpression_set.all()

        if start_date:
            queryset = queryset.filter(timestamp__gte=start_date)
        if end_date:
            queryset = queryset.filter(timestamp__lte=end_date)

        return queryset.count()

    def get_clicks_count(self, start_date=None, end_date=None):
        """
        Get clicks count with optional date filtering.

        Args:
            start_date: Start date for filtering (inclusive)
            end_date: End date for filtering (inclusive)

        Returns:
            Count of clicks within the date range
        """
        queryset = self.adclick_set.all()

        if start_date:
            queryset = queryset.filter(timestamp__gte=start_date)
        if end_date:
            queryset = queryset.filter(timestamp__lte=end_date)

        return queryset.count()

    def get_ctr(self, start_date=None, end_date=None):
        """
        Get CTR with optional date filtering.

        Args:
            start_date: Start date for filtering (inclusive)
            end_date: End date for filtering (inclusive)

        Returns:
            Click-through rate as a percentage
        """
        impressions = self.get_impressions_count(start_date, end_date)
        if impressions == 0:
            return 0

        clicks = self.get_clicks_count(start_date, end_date)
        return (clicks / impressions) * 100


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
