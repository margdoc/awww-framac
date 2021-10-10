from django.contrib.auth.models import AbstractUser

from framac.utils import Entity


class User(Entity, AbstractUser):
    def __str__(self):
        return f"{self.username}"
