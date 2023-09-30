"""
URL configuration for rulesbot project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path
from django.views.generic import TemplateView

from games.sitemaps import GamesSitemap
from pages import views as pages_views
from pages.sitemaps import PagesSitemap

urlpatterns = [
    path("", pages_views.LandingView.as_view(), name="index"),
    path("about/", pages_views.about_view, name="about"),
    path("terms/", pages_views.terms_view, name="terms"),
    path("games/", include("games.urls")),
    path("chat/", include("chat.urls")),
    path("users/", include("users.urls")),
    path("admin/", admin.site.urls),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": {"pages": PagesSitemap, "games": GamesSitemap}},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    path(
        "robots.txt",
        TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
        name="robots.txt",
    ),
]
