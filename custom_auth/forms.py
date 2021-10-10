from django import forms

from . import models


class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        required=True
    )
    password = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.PasswordInput()
    )


class CreateUserForm(LoginForm):
    repeat_password = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.PasswordInput()
    )

    def clean(self):
        cleaned_data = super().clean()

        username = cleaned_data.get("username")
        password = cleaned_data.get("password")
        repeated_password = cleaned_data.get("repeat_password")

        if password != repeated_password:
            raise forms.ValidationError("Password and repeated password don't match")

        if models.User.objects.filter(username=username).first() is not None:
            raise forms.ValidationError("Username is already taken")

        return cleaned_data
