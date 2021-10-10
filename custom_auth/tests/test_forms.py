from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils.crypto import get_random_string

from .. import forms
from ..models import User


class LoginFormTest(TestCase):
    def test_basic(self):
        form = forms.LoginForm(
            data={
                "username": get_random_string(10),
                "password": get_random_string(10)
            }
        )

        self.assertTrue(form.is_valid())

    def test_required_password(self):
        form = forms.LoginForm(
            data={
                "username": get_random_string(10),
            }
        )

        self.assertFalse(form.is_valid())

    def test_required_username(self):
        form = forms.LoginForm(
            data={
                "password": get_random_string(10),
            }
        )

        self.assertFalse(form.is_valid())


class CreateUserFormTest(TestCase):
    def test_basic(self):
        password = get_random_string(10)

        form = forms.LoginForm(
            data={
                "username": get_random_string(10),
                "password": password,
                "repeat_password": password
            }
        )

        self.assertTrue(form.is_valid())

    def test_different_passwords(self):
        form = forms.CreateUserForm(
            data={
                "username": get_random_string(10),
                "password": get_random_string(10),
                "repeat_password": get_random_string(10)
            }
        )

        self.assertFalse(form.is_valid())

    def test_required_username(self):
        form = forms.CreateUserForm(
            data={
                "password": get_random_string(10),
                "repeat_password": get_random_string(10)
            }
        )

        self.assertFalse(form.is_valid())

    def test_required_password(self):
        form = forms.CreateUserForm(
            data={
                "username": get_random_string(10),
                "repeat_password": get_random_string(10)
            }
        )

        self.assertFalse(form.is_valid())

    def test_required_repeated_password(self):
        form = forms.CreateUserForm(
            data={
                "username": get_random_string(10),
                "password": get_random_string(10),
            }
        )

        self.assertFalse(form.is_valid())

    def test_existing_user(self):
        username = get_random_string(10)
        User.objects.create_user(username=username, password=get_random_string(10))

        form = forms.CreateUserForm(
            data={
                "username": username,
                "password": get_random_string(10),
                "repeat_password": get_random_string(10)
            }
        )

        self.assertFalse(form.is_valid())
