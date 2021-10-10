from django.test.client import Client
from django.test import TestCase
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.contrib import auth

from ..models import User


class LoginViewTest(TestCase):
    def test_basic(self):
        client = Client()
        url = reverse("login")

        response = client.get(url, follow=True)
        self.assertContains(response, "Login")

        username = get_random_string(10)
        password = get_random_string(10)

        User.objects.create_user(
            username=username,
            password=password
        )

        response = client.post(url, data={
            "username": username,
            "password": password
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Home")

        response = client.get(reverse("logout"), data={
            "username": username,
            "password": password
        }, follow=True)

        self.assertNotContains(response, username)

    def test_incorrect_credentials(self):
        client = Client()
        url = reverse("login")

        User.objects.create_user(
            username=get_random_string(10),
            password=get_random_string(10)
        )

        response = client.post(url, data={
            "username": get_random_string(10),
            "password": get_random_string(10)
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Home")


class CreateUserViewTest(TestCase):
    def test_basic(self):
        client = Client()
        url = reverse("create_user")

        username = get_random_string(10)
        password = get_random_string(10)

        User.objects.create_superuser(
            username=username,
            password=password
        )

        client.login(username=username, password=password)

        response = client.get(url, follow=True)
        self.assertContains(response, "Create User")

        username = get_random_string(10)
        password = get_random_string(10)

        response = client.post(url, data={
            "username": username,
            "password": password,
            "repeat_password": password
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(User.objects.get(username=username))

        client.logout()

        response = client.post(reverse("login"), data={
            "username": get_random_string(10),
            "password": get_random_string(10)
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Home")
