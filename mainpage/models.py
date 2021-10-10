from django.db import models

from custom_auth.models import User
from framac.utils import Entity


class OwnedEntity(Entity):
    owner = models.ForeignKey(
        User,
        default=None,
        blank=False,
        on_delete=models.DO_NOTHING,
    )

    class Meta:
        abstract = True


class FileSystemEntity(OwnedEntity):
    name = models.CharField(
        max_length=20,
        default=None,
        blank=False
    )
    description = models.CharField(
        blank=True,
        default="",
        max_length=100
    )
    parent = models.ForeignKey(
        "Directory",
        null=True,
        default=None,
        blank=True,
        on_delete=models.DO_NOTHING
    )

    def __str__(self):
        return f"{self.parent if not self.parent is None else ''}/{self.name}"

    class Meta:
        abstract = True


class Directory(FileSystemEntity):
    pass


class File(FileSystemEntity):
    content = models.FileField(
        upload_to="files/"
    )


class SectionCategory(models.TextChoices):
    Procedure = "Procedure"
    Property = "Property"
    Lemma = "Lemma"
    Assertion = "Assertion"
    Invariant = "Invariant"
    Precondition = "Precondition"
    PostCondition = "PostCondition"


class SectionStatus(models.TextChoices):
    Proved = "Proved"
    Invalid = "Invalid"
    CounterExample = "CounterExample"
    Unchecked = "Unchecked"


class StatusData(Entity):
    status = models.CharField(
        max_length=256,
        default=None,
        blank=False
    )
    author = models.ForeignKey(
        User,
        on_delete=models.DO_NOTHING,
    )

    def __str__(self):
        return f"{self.status} - {self.author}"


class FileSection(Entity):
    name = models.CharField(
        blank=True,
        default="",
        max_length=20
    )
    description = models.CharField(
        blank=True,
        default="",
        max_length=100
    )
    category = models.CharField(
        max_length=20,
        blank=False,
        default=None,
        choices=SectionCategory.choices
    )
    status = models.CharField(
        max_length=256,
        choices=SectionStatus.choices,
        default=SectionStatus.Unchecked
    )
    line = models.IntegerField()
    statusData = models.ForeignKey(
        StatusData,
        null=True,
        blank=True,
        default=None,
        on_delete=models.CASCADE,
    )
    file = models.ForeignKey(
        File,
        on_delete=models.DO_NOTHING
    )

    def __str__(self):
        return f"{str(self.file)}::{self.name} ({self.line})"
