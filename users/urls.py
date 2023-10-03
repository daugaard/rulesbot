from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

app_name = "users"
urlpatterns = [
    path("", views.account_view, name="account"),
    path("sign-up", views.sign_up_view, name="sign-up"),
    path("login", views.login_view, name="login"),
    path("account", views.account_view, name="account"),
    path("change-password", views.change_password_view, name="change-password"),
    path("logout", LogoutView.as_view(), name="logout"),
]
