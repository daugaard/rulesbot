from django.test import TestCase


# Create your tests here.
class TestViews(TestCase):
    def test_get_signup_page(self):
        response = self.client.get("/users/sign-up")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/sign_up.html")

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
