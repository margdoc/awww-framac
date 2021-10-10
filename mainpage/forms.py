from django import forms

from custom_auth.models import User
from . import models


class FileSystemEntityAdd(forms.ModelForm):
    parent = forms.ModelChoiceField(
        queryset=models.Directory.objects.filter(
            validity=True
        ),
        empty_label="/",
        required=False
    )

    def __init__(self, user: User, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not user.is_anonymous:
            self.fields["parent"].queryset = models.Directory.objects.filter(
                validity=True,
                owner=user
            )


class FileFormAdd(FileSystemEntityAdd):
    class Meta:
        model = models.File
        fields = ['name', 'description', 'content', 'parent']


class FileFormDelete(forms.Form):
    file = forms.ModelChoiceField(
        queryset=models.File.objects.filter(
            validity=True
        )
    )

    def __init__(self, user: User, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not user.is_anonymous:
            self.fields["file"].queryset = models.File.objects.filter(
                validity=True,
                owner=user
            )


class DirectoryFormAdd(FileSystemEntityAdd):
    class Meta:
        model = models.Directory
        fields = ['name', 'description', 'parent']


class DirectoryFormDelete(forms.Form):
    directory = forms.ModelChoiceField(
        queryset=models.Directory.objects.filter(
            validity=True
        )
    )

    def __init__(self, user: User, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not user.is_anonymous:
            self.fields["directory"].queryset = models.Directory.objects.filter(
                validity=True,
                owner=user
            )


class VCS(forms.Form):
    rte = forms.BooleanField(
        required=False
    )
    props = forms.CharField(
        required=False
    )
