from django.test import TestCase
from django.utils.crypto import get_random_string

from custom_auth.models import User
from .. import models


class TestCaseWithUser(TestCase):
    username = None
    user = None

    @classmethod
    def setUpTestData(cls):
        cls.username = get_random_string(length=10)

        User.objects.create(
            username=cls.username,
            password=get_random_string(length=10)
        )

    def setUp(self):
        self.user = User.objects.get(username=self.__class__.username)
        self.assertIsNotNone(self.user)


class TestCaseWithFileSystem(TestCaseWithUser):
    parent_name = None
    parent_dir = None

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.parent_name = get_random_string(length=10)

        models.Directory.objects.create(
            name=cls.parent_name,
            owner=User.objects.get(username=cls.username)
        )

    def setUp(self):
        super().setUp()
        self.parent_dir = models.Directory.objects.get(name=self.__class__.parent_name)
        self.assertIsNotNone(self.parent_dir)