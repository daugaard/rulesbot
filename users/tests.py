from django.contrib.auth.models import User
from django.test import TestCase


# Create your tests here.
class TestViews(TestCase):
    def test_get_signup_page(self):
        response = self.client.get("/users/sign-up")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/sign_up.html")

    def test_post_signup_page(self):
        self.assertEqual(User.objects.count(), 0)
        response = self.client.post(
            "/users/sign-up",
            {
                "username": "testuser",
                "email": "test@email.com",
                "password": "testpassword",
                "confirm_password": "testpassword",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/users/account")

        user = User.objects.get(username="testuser")
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "test@email.com")

    def test_post_signup_page_with_existing_username(self):
        User.objects.create_user(
            username="testuser", email="test@email.com", password="testpassword"
        )
        response = self.client.post(
            "/users/sign-up",
            {
                "username": "testuser",
                "email": "test@email2.com",
                "password": "testpassword",
                "confirm_password": "testpassword",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/sign_up.html")
        self.assertFormError(response, "form", "username", "Username already exists")

    def test_post_signup_page_with_existing_email(self):
        User.objects.create_user(
            username="testuser", email="test@email.com", password="testpassword"
        )
        response = self.client.post(
            "/users/sign-up",
            {
                "username": "testuser2",
                "email": "test@email.com",
                "password": "testpassword",
                "confirm_password": "testpassword",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/sign_up.html")
        self.assertFormError(response, "form", "email", "Email already exists")

    def test_get_login_page(self):
        response = self.client.get("/users/login")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/login.html")

    def test_get_account_page(self):
        response = self.client.get("/users/account")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/users/login?next=/users/account")

    def test_get_logout_page(self):
        response = self.client.get("/users/logout")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/")
