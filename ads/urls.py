"""
URL configuration for ads app.
"""

from django.urls import path

from ads import views

app_name = "ads"

urlpatterns = [
    # Click tracking endpoint (to be implemented in Phase 3)
    path("click/<int:ad_id>/", views.ad_click_redirect, name="click"),
]
