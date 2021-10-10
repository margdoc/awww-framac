from django.db import IntegrityError
from django.utils.crypto import get_random_string

import random

from .. import models
from .utils import TestCaseWithUser, TestCaseWithFileSystem


class DirectoryTest(TestCaseWithUser):
    def test_missing_name(self):
        with self.assertRaises(IntegrityError):
            models.Directory.objects.create(
                description=get_random_string(length=20),
                parent=None,
                owner=self.user
            )

    def test_missing_owner(self):
        with self.assertRaises(IntegrityError):
            models.Directory.objects.create(
                description=get_random_string(length=20),
                parent=None,
                name=get_random_string(length=10)
            )

    def test_basic(self):
        parent_name = get_random_string(length=10)
        dir_name = get_random_string(length=10)

        parent_dir = models.Directory.objects.create(
            name=parent_name,
            owner=self.user
        )

        self.assertEqual(str(parent_dir), f"/{parent_name}")
        self.assertIsNone(parent_dir.parent)

        directory = models.Directory.objects.create(
            name=dir_name,
            parent=parent_dir,
            owner=self.user
        )

        self.assertEqual(str(directory), f"/{parent_name}/{dir_name}")
        self.assertEqual(directory.name, dir_name)
        self.assertEqual(directory.parent, parent_dir)
        self.assertEqual(directory.owner, self.user)
        self.assertTrue(directory.validity)


class FileTest(TestCaseWithFileSystem):
    def test_missing_name(self):
        with self.assertRaises(IntegrityError):
            models.File.objects.create(
                description=get_random_string(length=20),
                parent=None,
                owner=self.user
            )

    def test_missing_owner(self):
        with self.assertRaises(IntegrityError):
            models.File.objects.create(
                description=get_random_string(length=20),
                parent=None,
                name=get_random_string(length=10)
            )

    def test_basic(self):
        file_name = get_random_string(length=10)

        file = models.File.objects.create(
            name=file_name,
            parent=self.parent_dir,
            owner=self.user
        )

        self.assertEqual(str(file), f"/{self.parent_dir.name}/{file_name}")
        self.assertEqual(file.name, f"{file_name}")
        self.assertEqual(file.parent, self.parent_dir)
        self.assertEqual(file.owner, self.user)
        self.assertTrue(file.validity)


class StatusDataTest(TestCaseWithUser):
    def test_missing_author(self):
        with self.assertRaises(IntegrityError):
            models.StatusData.objects.create(
                status="test"
            )

    def test_missing_status(self):
        with self.assertRaises(IntegrityError):
            models.StatusData.objects.create(
                author=self.user
            )

    def test_basic(self):
        status = get_random_string(length=100)

        data = models.StatusData.objects.create(
            status=status,
            author=self.user
        )

        self.assertEqual(data.status, status)
        self.assertEqual(data.author, self.user)
        self.assertTrue(data.validity)


class FileSectionTest(TestCaseWithUser):
    def test_basic(self):
        name = get_random_string(length=10)
        description = get_random_string(length=100)
        line = random.randint(1, 100)
        category = random.choice(list(models.SectionCategory))
        status = random.choice(list(models.SectionStatus))

        file_name = get_random_string(length=10)
        file = models.File.objects.create(
            name=file_name,
            owner=self.user
        )

        section = models.FileSection.objects.create(
            name=name,
            description=description,
            line=line,
            category=category,
            file=file,
            status=status
        )

        self.assertEqual(section.name, name)
        self.assertEqual(section.description, description)
        self.assertEqual(section.line, line)
        self.assertEqual(section.category, category)
        self.assertEqual(section.status, status)
        self.assertEqual(section.file, file)
        self.assertIsNone(section.statusData)
        self.assertTrue(section.validity)

    def test_optional_fields(self):
        line = random.randint(1, 100)
        category = random.choice(list(models.SectionCategory))

        file_name = get_random_string(length=10)
        file = models.File.objects.create(
            name=file_name,
            owner=self.user
        )

        section = models.FileSection.objects.create(
            line=line,
            category=category,
            file=file
        )

        self.assertEqual(section.line, line)
        self.assertEqual(section.category, category)
        self.assertEqual(section.file, file)
        self.assertIsNone(section.statusData)

        self.assertEqual(section.name, "")
        self.assertEqual(section.description, "")
        self.assertEqual(section.status, models.SectionStatus.Unchecked)

    def test_category_required(self):
        name = get_random_string(length=10)
        description = get_random_string(length=100)
        line = random.randint(1, 100)

        file_name = get_random_string(length=10)
        file = models.File.objects.create(
            name=file_name,
            owner=self.user
        )

        with self.assertRaises(IntegrityError):
            models.FileSection.objects.create(
                name=name,
                description=description,
                line=line,
                file=file
            )

    def test_file_required(self):
        name = get_random_string(length=10)
        description = get_random_string(length=100)
        line = random.randint(1, 100)
        category = random.choice(list(models.SectionCategory))

        with self.assertRaises(IntegrityError):
            models.FileSection.objects.create(
                name=name,
                description=description,
                line=line,
                category=category
            )

    def test_line_required(self):
        name = get_random_string(length=10)
        description = get_random_string(length=100)
        category = random.choice(list(models.SectionCategory))

        file_name = get_random_string(length=10)
        file = models.File.objects.create(
            name=file_name,
            owner=self.user
        )

        with self.assertRaises(IntegrityError):
            models.FileSection.objects.create(
                name=name,
                description=description,
                category=category,
                file=file
            )
