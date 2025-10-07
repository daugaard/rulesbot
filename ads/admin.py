from datetime import timedelta

from django.contrib import admin
from django.shortcuts import render
from django.urls import path, reverse
from django.utils import timezone

from .models import Ad


class AdAdmin(admin.ModelAdmin):
    list_display = ("title", "game", "weight", "created_at", "updated_at")
    list_filter = ("game", "weight", "created_at")
    search_fields = ("title", "description")
    readonly_fields = ("created_at", "updated_at")

    def changelist_view(self, request, extra_context=None):
        """Override changelist to add analytics button"""
        extra_context = extra_context or {}
        extra_context["analytics_url"] = reverse("admin:ads_ad_analytics")
        return super().changelist_view(request, extra_context)

    def get_queryset(self, request):
        # Optimize query with select_related
        return super().get_queryset(request).select_related("game")

    def get_urls(self):
        """Add custom analytics URL to admin"""
        urls = super().get_urls()
        custom_urls = [
            path(
                "analytics/",
                self.admin_site.admin_view(self.analytics_view),
                name="ads_ad_analytics",
            ),
        ]
        return custom_urls + urls

    def analytics_view(self, request):
        """Custom analytics dashboard view"""
        # Get time period filter from query params (default to 'all')
        period = request.GET.get("period", "all")

        # Calculate date range based on period
        end_date = timezone.now()
        if period == "7days":
            start_date = end_date - timedelta(days=7)
            period_label = "Last 7 Days"
        elif period == "30days":
            start_date = end_date - timedelta(days=30)
            period_label = "Last 30 Days"
        else:
            start_date = None
            period_label = "All Time"

        # Get all ads with metrics
        ads = Ad.objects.select_related("game").all()

        # Calculate metrics for each ad
        analytics_data = []
        for ad in ads:
            impressions = ad.get_impressions_count(start_date, end_date)
            clicks = ad.get_clicks_count(start_date, end_date)
            ctr = ad.get_ctr(start_date, end_date)

            analytics_data.append(
                {
                    "ad": ad,
                    "impressions": impressions,
                    "clicks": clicks,
                    "ctr": ctr,
                }
            )

        context = {
            **self.admin_site.each_context(request),
            "title": "Ad Analytics",
            "analytics_data": analytics_data,
            "current_period": period,
            "period_label": period_label,
            "opts": self.model._meta,
        }

        return render(request, "admin/ads/analytics.html", context)


admin.site.register(Ad, AdAdmin)
