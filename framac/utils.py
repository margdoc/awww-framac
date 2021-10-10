from django.db import models


class Entity(models.Model):
    validity = models.BooleanField(
        default=True
    )
    timestamp = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        abstract = True
