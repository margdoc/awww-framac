from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.core.files import File
from django.contrib.auth.decorators import login_required as django_login_required
import re

from custom_auth.models import User
from . import models, forms, framac, config


def login_required(f):
    return django_login_required(f, login_url="login")


class FileDisplay:
    pk: int
    name: str

    def __init__(self, file: models.File):
        self.pk = file.pk
        self.name = file.name


class DirectoryDisplay:
    pk: int
    name: str
    files: [FileDisplay]
    subdirectories: ["DirectoryDisplay"]

    def __init__(self, user: User, directory: models.Directory):
        self.pk = directory.pk
        self.name = directory.name

        self.files = [
            FileDisplay(file) for file in models.File.objects.filter(
                parent=directory.pk,
                validity=True,
                owner=user
            )
        ]

        self.subdirectories = [
            DirectoryDisplay(user, sub_directory) for sub_directory in models.Directory.objects.filter(
                parent=directory.pk,
                validity=True,
                owner=user
            )
        ]


def root_directories(user: User) -> [DirectoryDisplay]:
    if user.is_anonymous:
        return []

    return [
        DirectoryDisplay(user, directory) for directory in models.Directory.objects.filter(
            parent=None,
            validity=True,
            owner=user
        )
    ]


def root_files(user: User) -> [FileDisplay]:
    if user.is_anonymous:
        return []

    return [
        FileDisplay(file) for file in models.File.objects.filter(
            parent=None,
            validity=True,
            owner=user
        )
    ]


def base_context(request: HttpRequest):
    tab = request.GET.get("tab", config.DEFAULTS["tab"])

    return {
        "directories": root_directories(request.user),
        "files": root_files(request.user),
        "tab": tab,
        "provers": config.PROVERS.keys()
    }


def index(request: HttpRequest, forms_context=None) -> HttpResponse:
    forms_context = {
        "vcs_form": forms.VCS(),
        "file_add_form": forms.FileFormAdd(request.user),
        "file_delete_form": forms.FileFormDelete(request.user),
        "directory_add_form": forms.DirectoryFormAdd(request.user),
        "directory_delete_form": forms.DirectoryFormDelete(request.user),
        **(forms_context if forms_context is not None else {})
    }

    if request.method == "POST":
        form = forms.VCS(request.POST)

        if form.is_valid():
            request.session["rte"] = form.cleaned_data["rte"]
            request.session["props"] = form.cleaned_data["props"]

    context = {
        **base_context(request),
        **forms_context
    }

    return render(request, "mainpage/index.html", context)


def file_get(request: HttpRequest, file_pk: int) -> dict:
    file = models.File.objects.get(pk=file_pk)

    if file.owner != request.user:
        raise PermissionDenied("You have to be owner to see this file")

    with file.content.open(mode="r") as content:
        code = re.sub('\\n', '\n', ''.join(content.readlines()))

    return {
        "code": code,
        "result": framac.get_result(file_pk),
        "program_elements": framac.get_output(file_pk)
    }


@login_required
def file_get_endpoint(request: HttpRequest, file_pk: int) -> JsonResponse:
    return JsonResponse(file_get(request, file_pk))


def rerun(request: HttpRequest, file_pk: int):
    file = models.File.objects.get(pk=file_pk)
    framac.verification(
        file.content.path,
        file_pk,
        request.COOKIES.get("prover", config.DEFAULTS["prover"]),
        request.session.get("props", ""),
        request.session.get("rte", False)
    )


def generate_program_elements(request: HttpRequest, file_pk: int):
    for section in models.FileSection.objects.filter(file__id=file_pk):
        if section.statusData is not None:
            section.statusData.delete()
            section.statusData = None
            section.status = models.SectionStatus.Unchecked
            section.save()

    output = framac.parse_output(file_pk)

    for (data, line, result) in output:
        try:
            section = models.FileSection.objects.get(file__id=file_pk, line=line)

            status_data = models.StatusData(
                status=data,
                author=request.user
            )
            status_data.save()

            section.statusData = status_data
            section.status = result
            section.save()

        except models.FileSection.DoesNotExist:
            continue


@login_required
def file_rerun(request: HttpRequest, file_pk: int) -> JsonResponse:
    rerun(request, file_pk)
    return JsonResponse({
        "result": framac.get_result(file_pk)
    })


def file_uploaded(request: HttpRequest, file: models.File):
    models.FileSection.objects.filter(file__pk=file.pk).delete()

    for (line, category) in framac.parse_file(file.pk):
        section = models.FileSection(
            name=str(category),
            description="",
            category=category,
            line=line,
            file=file,
            statusData=None
        )
        section.save()

    framac.result(file.content.path, file.pk)
    generate_program_elements(request, file.pk)


@login_required
def file_change(request: HttpRequest, file_pk: int) -> HttpResponse:
    file_content = request.POST["file"]

    file = models.File.objects.get(pk=file_pk)

    with open(file.content.path, "w") as f:
        file_data = File(f)
        file_data.write(file_content)

    file_uploaded(request, file)

    return file_get_endpoint(request, file_pk)


@login_required
def file_add(request: HttpRequest) -> HttpResponse:
    form = forms.FileFormAdd(request.user, request.POST, request.FILES)
    if form.is_valid():
        post = form.save(commit=False)

        file = form.instance
        file.owner = request.user

        post.save()

        file_uploaded(request, file)

        return redirect("index")

    return index(request, forms_context={
        "file_add_form": form
    })


@login_required
def file_delete(request: HttpRequest) -> HttpResponse:
    form = forms.FileFormDelete(request.user, request.POST)
    if form.is_valid():
        instance = form.cleaned_data['file']
        instance.validity = False
        instance.save()

        return redirect("index")

    return index(request, forms_context={
        "file_delete_form": form
    })


@login_required
def directory_add(request: HttpRequest) -> HttpResponse:
    form = forms.DirectoryFormAdd(request.user, request.POST)
    if form.is_valid():
        post = form.save(commit=False)

        directory = form.instance
        directory.owner = request.user

        post.save()
        return redirect("index")

    return index(request, forms_context={
        "directory_add_form": form
    })


@login_required
def directory_delete(request: HttpRequest) -> HttpResponse:
    form = forms.DirectoryFormDelete(request.user, request.POST)
    if form.is_valid():
        instance = form.cleaned_data['directory']
        instance.validity = False

        def delete_all_children(directories: [models.Directory]):
            models.File.objects.filter(parent__in=directories).update(validity=False)

            next_dirs = models.Directory.objects.filter(parent__in=directories, validity=True)

            if next_dirs:
                delete_all_children(next_dirs)
                next_dirs.update(validity=False)

        instance.save()
        delete_all_children([instance])
        return redirect("index")

    return index(request, forms_context={
        "directory_delete_form": form
    })
