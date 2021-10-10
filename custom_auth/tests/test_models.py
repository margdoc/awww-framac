from django.db import IntegrityError
from django.test import TestCase
from django.utils.crypto import get_random_string
from django.contrib.auth import authenticate

import random

from ..models import User


class UserTest(TestCase):
    def test_basic(self):
        username = get_random_string(10)
        password = get_random_string(10)

        User.objects.create_user(
            username=username,
            password=password
        )

        self.assertEqual(
            username,
            User.objects.get(username=username).username
        )
        self.assertIsNotNone(
            authenticate(username=username, password=password)
        )
        self.assertIsNone(
            authenticate(username=username, password=get_random_string(9))
        )
        self.assertIsNone(
            authenticate(username=get_random_string(9), password=password)
        )

