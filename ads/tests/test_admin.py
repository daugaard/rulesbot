from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from ads.models import Ad, AdClick, AdImpression
from games.models import Game


class AdAnalyticsAdminTest(TestCase):
    """Tests for ad analytics admin view"""

    def setUp(self):
        User = get_user_model()
        self.admin_user = User.objects.create_superuser(
            username="admin", email="admin@test.com", password="password"
        )
        self.client.login(username="admin", password="password")

        self.game = Game.objects.create(name="Test Game", ingested=True)

    def test_analytics_view_accessible(self):
        """Test that analytics view is accessible to admin users"""
        response = self.client.get("/admin/ads/ad/analytics/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ad Analytics")

    def test_analytics_view_requires_authentication(self):
        """Test that analytics view requires admin authentication"""
        self.client.logout()
        response = self.client.get("/admin/ads/ad/analytics/")

        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/admin/login/"))

    def test_analytics_view_all_time_default(self):
        """Test that analytics view defaults to 'all time' period"""
        ad = Ad.objects.create(
            title="Test Ad",
            description="Test description",
            link="https://example.com/product",
            game=self.game,
        )

        # Create some impressions and clicks
        for _ in range(5):
            AdImpression.objects.create(ad=ad)
        for _ in range(2):
            AdClick.objects.create(ad=ad)

        response = self.client.get("/admin/ads/ad/analytics/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "All Time")
        self.assertContains(response, "Test Ad")
        self.assertContains(response, "5")  # impressions
        self.assertContains(response, "2")  # clicks

    def test_analytics_view_last_7_days_filter(self):
        """Test analytics view with 7 days filter"""
        ad = Ad.objects.create(
            title="Test Ad",
            description="Test description",
            link="https://example.com/product",
            game=self.game,
        )

        # Create impressions from 10 days ago
        old_impression = AdImpression.objects.create(ad=ad)
        old_impression.timestamp = timezone.now() - timedelta(days=10)
        old_impression.save()

        # Create recent impressions (within 7 days)
        for _ in range(3):
            AdImpression.objects.create(ad=ad)

        response = self.client.get("/admin/ads/ad/analytics/?period=7days")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Last 7 Days")
        self.assertContains(response, "Test Ad")
        # Should show 3 recent impressions, not the old one
        context_data = [
            item
            for item in response.context["analytics_data"]
            if item["ad"].id == ad.id
        ]
        self.assertEqual(len(context_data), 1)
        self.assertEqual(context_data[0]["impressions"], 3)

    def test_analytics_view_last_30_days_filter(self):
        """Test analytics view with 30 days filter"""
        ad = Ad.objects.create(
            title="Test Ad",
            description="Test description",
            link="https://example.com/product",
            game=self.game,
        )

        # Create impressions from 35 days ago
        old_impression = AdImpression.objects.create(ad=ad)
        old_impression.timestamp = timezone.now() - timedelta(days=35)
        old_impression.save()

        # Create recent impressions (within 30 days)
        for _ in range(4):
            AdImpression.objects.create(ad=ad)

        response = self.client.get("/admin/ads/ad/analytics/?period=30days")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Last 30 Days")
        self.assertContains(response, "Test Ad")
        # Should show 4 recent impressions, not the old one
        context_data = [
            item
            for item in response.context["analytics_data"]
            if item["ad"].id == ad.id
        ]
        self.assertEqual(len(context_data), 1)
        self.assertEqual(context_data[0]["impressions"], 4)

    def test_analytics_view_ctr_calculation(self):
        """Test that CTR is calculated correctly in analytics view"""
        ad = Ad.objects.create(
            title="Test Ad",
            description="Test description",
            link="https://example.com/product",
            game=self.game,
        )

        # Create 10 impressions and 3 clicks (30% CTR)
        for _ in range(10):
            AdImpression.objects.create(ad=ad)
        for _ in range(3):
            AdClick.objects.create(ad=ad)

        response = self.client.get("/admin/ads/ad/analytics/")

        self.assertEqual(response.status_code, 200)
        context_data = [
            item
            for item in response.context["analytics_data"]
            if item["ad"].id == ad.id
        ]
        self.assertEqual(len(context_data), 1)
        self.assertEqual(context_data[0]["ctr"], 30.0)

    def test_analytics_view_multiple_ads(self):
        """Test analytics view displays multiple ads correctly"""
        ad1 = Ad.objects.create(
            title="Ad 1",
            description="Description 1",
            link="https://example.com/1",
            game=self.game,
        )
        ad2 = Ad.objects.create(
            title="Ad 2",
            description="Description 2",
            link="https://example.com/2",
        )

        # Create different metrics for each ad
        for _ in range(5):
            AdImpression.objects.create(ad=ad1)
        for _ in range(1):
            AdClick.objects.create(ad=ad1)

        for _ in range(10):
            AdImpression.objects.create(ad=ad2)
        for _ in range(2):
            AdClick.objects.create(ad=ad2)

        response = self.client.get("/admin/ads/ad/analytics/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ad 1")
        self.assertContains(response, "Ad 2")

        analytics_data = response.context["analytics_data"]
        self.assertEqual(len(analytics_data), 2)

    def test_analytics_view_no_ads(self):
        """Test analytics view when no ads exist"""
        response = self.client.get("/admin/ads/ad/analytics/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No ads found")

    def test_analytics_template_rendering(self):
        """Test that analytics template renders correctly"""
        ad = Ad.objects.create(
            title="Test Ad",
            description="Test description",
            link="https://example.com/product",
            game=self.game,
        )

        AdImpression.objects.create(ad=ad)
        AdClick.objects.create(ad=ad)

        response = self.client.get("/admin/ads/ad/analytics/")

        self.assertEqual(response.status_code, 200)
        # Check for time period filters
        self.assertContains(response, "Last 7 Days")
        self.assertContains(response, "Last 30 Days")
        self.assertContains(response, "All Time")
        # Check for table headers
        self.assertContains(response, "Ad Title")
        self.assertContains(response, "Game")
        self.assertContains(response, "Impressions")
        self.assertContains(response, "Clicks")
        self.assertContains(response, "CTR")
        # Check for ad data
        self.assertContains(response, "Test Ad")

    def test_analytics_view_time_filtered_clicks(self):
        """Test that clicks are also filtered by time period"""
        ad = Ad.objects.create(
            title="Test Ad",
            description="Test description",
            link="https://example.com/product",
            game=self.game,
        )

        # Create old clicks
        old_click = AdClick.objects.create(ad=ad)
        old_click.timestamp = timezone.now() - timedelta(days=10)
        old_click.save()

        # Create recent clicks (within 7 days)
        for _ in range(2):
            AdClick.objects.create(ad=ad)

        response = self.client.get("/admin/ads/ad/analytics/?period=7days")

        self.assertEqual(response.status_code, 200)
        context_data = [
            item
            for item in response.context["analytics_data"]
            if item["ad"].id == ad.id
        ]
        self.assertEqual(len(context_data), 1)
        # Should only count the 2 recent clicks
        self.assertEqual(context_data[0]["clicks"], 2)
