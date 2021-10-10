from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import auth

from . import forms
from . import models


@staff_member_required
def create_user(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = forms.CreateUserForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            user = models.User.objects.create_user(username=username, password=password)
            user.save()

            return redirect("index")
    else:
        form = forms.CreateUserForm()

    context = {
        "form": form
    }

    return render(request, "custom_auth/create_user.html", context)


def login(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = forms.LoginForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            user = auth.authenticate(request, username=username, password=password)

            if user is not None:
                auth.login(request, user)
                return redirect(request.GET.get("next", "index"))
            else:
                form.add_error("password", "Authentication failed")
    else:
        form = forms.LoginForm()

    context = {
        "form": form
    }

    return render(request, "custom_auth/login.html", context)


def logout(request: HttpRequest) -> HttpResponse:
    auth.logout(request)
    return redirect("index")
