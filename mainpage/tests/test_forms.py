from django.utils.crypto import get_random_string
from django.core.files.uploadedfile import SimpleUploadedFile

from .. import forms
from .. import models
from .utils import TestCaseWithFileSystem


class FileFormAddTest(TestCaseWithFileSystem):
    def test_basic(self):
        name = get_random_string(10)
        description = get_random_string(10)
        content = SimpleUploadedFile(
            get_random_string(10),
            str.encode(get_random_string(100))
        )

        form = forms.FileFormAdd(
            self.user,
            data={
                "name": name,
                "description": description,
                "parent": self.parent_dir
            },
            files={
                "content": content
            }
        )

        self.assertTrue(form.is_valid())

        instance = form.instance

        self.assertEqual(instance.name, name)
        self.assertEqual(instance.description, description)
        self.assertEqual(instance.content, content)
        self.assertEqual(instance.parent, self.parent_dir)

    def test_optional_fields(self):
        name = get_random_string(10)
        content = SimpleUploadedFile(
            get_random_string(10),
            str.encode(get_random_string(100))
        )

        form = forms.FileFormAdd(
            self.user,
            data={
                "name": name,
            },
            files={
                "content": content
            }
        )

        self.assertTrue(form.is_valid())

        instance = form.instance

        self.assertEqual(instance.name, name)
        self.assertEqual(instance.description, "")
        self.assertEqual(instance.content, content)
        self.assertIsNone(instance.parent)

    def test_required_name(self):
        description = get_random_string(10)
        content = SimpleUploadedFile(
            get_random_string(10),
            str.encode(get_random_string(100))
        )

        form = forms.FileFormAdd(
            self.user,
            data={
                "description": description,
                "parent": self.parent_dir
            },
            files={
                "content": content
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn(
            "This field is required.",
            form.errors["name"]
        )

    def test_required_content(self):
        name = get_random_string(10)
        description = get_random_string(10)

        form = forms.FileFormAdd(
            self.user,
            data={
                "name": name,
                "description": description,
                "parent": self.parent_dir
            },
        )

        self.assertFalse(form.is_valid())
        self.assertIn(
            "This field is required.",
            form.errors["content"]
        )


class DirectoryFormAddTest(TestCaseWithFileSystem):
    def test_basic(self):
        name = get_random_string(10)
        description = get_random_string(10)

        form = forms.DirectoryFormAdd(
            self.user,
            data={
                "name": name,
                "description": description,
                "parent": self.parent_dir
            }
        )

        self.assertTrue(form.is_valid())

        instance = form.instance

        self.assertEqual(instance.name, name)
        self.assertEqual(instance.description, description)
        self.assertEqual(instance.parent, self.parent_dir)

    def test_required_name(self):
        description = get_random_string(10)

        form = forms.DirectoryFormAdd(
            self.user,
            data={
                "description": description,
                "parent": self.parent_dir
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn(
            "This field is required.",
            form.errors["name"]
        )


class FileFormDeleteTest(TestCaseWithFileSystem):
    def test_basic(self):
        file = models.File.objects.create(
            name=get_random_string(length=10),
            parent=self.parent_dir,
            owner=self.user
        )

        form = forms.FileFormDelete(
            self.user,
            data={
                "file": file
            }
        )

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["file"], file)

    def test_required_field(self):
        form = forms.FileFormDelete(
            self.user
        )
        self.assertFalse(form.is_valid())


class DirectoryFormDeleteTest(TestCaseWithFileSystem):
    def test_basic(self):
        directory = models.Directory.objects.create(
            name=get_random_string(length=10),
            parent=self.parent_dir,
            owner=self.user
        )

        form = forms.DirectoryFormDelete(
            self.user,
            data={
                "directory": directory
            }
        )

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["directory"], directory)

    def test_required_field(self):
        form = forms.DirectoryFormDelete(
            self.user
        )
        self.assertFalse(form.is_valid())
