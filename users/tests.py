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

    def test_post_signup_page_with_non_matching_password(self):
        response = self.client.post(
            "/users/sign-up",
            {
                "username": "testuser2",
                "email": "test@email.com",
                "password": "testpassword",
                "confirm_password": "testpassword-wrong",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/sign_up.html")
        self.assertFormError(
            response, "form", "confirm_password", "Passwords do not match"
        )

    def test_signup_user_cannot_access_admin(self):
        self.client.post(
            "/users/sign-up",
            {
                "username": "testuser",
                "email": "test@email.com",
                "password": "testpassword",
                "confirm_password": "testpassword",
            },
        )
        self.client.login(username="testuser", password="testpassword")
        response = self.client.get("/admin/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/admin/login/?next=/admin/")
        response = self.client.get("/users/account")
        self.assertEqual(response.status_code, 200)

    def test_get_login_page(self):
        response = self.client.get("/users/login")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/login.html")

    def test_login_correct_password(self):
        User.objects.create_user(
            username="testuser", email="test@email.com", password="test"
        )
        response = self.client.post(
            "/users/login",
            {"email": "test@email.com", "password": "test", "next": "/some-url"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/some-url")

    def test_login_wrong_password(self):
        User.objects.create_user(
            username="testuser", email="test@email.com", password="test"
        )
        response = self.client.post(
            "/users/login",
            {
                "email": "test@email.com",
                "password": "other-password",
                "next": "/some-url",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/login.html")

    def test_get_account_page(self):
        response = self.client.get("/users/account")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/users/login?next=/users/account")

    def test_get_account_page_after_login(self):
        User.objects.create_user(
            username="testuser", email="test@email.com", password="test"
        )
        response = self.client.post(
            "/users/login",
            {"email": "test@email.com", "password": "test", "next": "/users/account"},
        )
        self.assertEqual(response.status_code, 302)
        response = self.client.get("/users/account")
        self.assertEqual(response.status_code, 200)

    def test_get_logout_page(self):
        response = self.client.get("/users/logout")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/")

    def test_get_logout_page_after_login(self):
        User.objects.create_user(username="testuser", email="test", password="test")
        self.client.login(username="testuser", password="test")
        response = self.client.get("/users/account")
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/users/logout")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/")

        response = self.client.get("/users/account")
        self.assertEqual(response.status_code, 302)

    def test_get_change_password_page(self):
        response = self.client.get("/users/change-password")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/users/login?next=/users/change-password")

    def test_get_change_password_page_after_login(self):
        User.objects.create_user(username="testuser", email="test", password="test")
        self.client.login(username="testuser", password="test")
        response = self.client.get("/users/change-password")
        self.assertEqual(response.status_code, 200)

    def test_post_change_password_page(self):
        User.objects.create_user(username="testuser", email="test", password="test")
        self.client.login(username="testuser", password="test")
        response = self.client.post(
            "/users/change-password",
            {
                "current_password": "test",
                "new_password": "newpassword",
                "confirm_new_password": "newpassword",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/users/account")

        user = User.objects.get(username="testuser")
        self.assertTrue(user.check_password("newpassword"))

    def test_post_change_password_page_with_wrong_current_password(self):
        User.objects.create_user(username="testuser", email="test", password="test")
        self.client.login(username="testuser", password="test")
        response = self.client.post(
            "/users/change-password",
            {
                "current_password": "wrongpassword",
                "new_password": "newpassword",
                "confirm_new_password": "newpassword",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/change_password.html")
        self.assertFormError(response, "form", "current_password", "Incorrect password")

    def test_post_change_password_page_with_non_matching_passwords(self):
        User.objects.create_user(username="testuser", email="test", password="test")
        self.client.login(username="testuser", password="test")
        response = self.client.post(
            "/users/change-password",
            {
                "current_password": "test",
                "new_password": "newpassword",
                "confirm_new_password": "newpassword-wrong",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/change_password.html")
        self.assertFormError(
            response,
            "form",
            "confirm_new_password",
            "Passwords do not match",
        )
