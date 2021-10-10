from django.test.client import Client
from django.test import TestCase
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.core.files.uploadedfile import SimpleUploadedFile
import random

from custom_auth.models import User
from .. import models


class TestCaseRandomApp(TestCase):
    url = reverse("index")
    client: Client = None

    example_user: str = None
    example_user_password: str = None
    example_admin: str = None
    example_admin_password: str = None

    def login_as_user(self):
        self.assertTrue(self.client.login(
            username=self.example_user,
            password=self.example_user_password
        ))

    def login_as_admin(self):
        self.assertTrue(self.client.login(
            username=self.example_admin,
            password=self.example_admin_password
        ))

    def logout(self):
        self.client.logout()

    def setUp(self):
        self.example_user = get_random_string(10)
        self.example_user_password = get_random_string(10)
        self.example_admin = get_random_string(10)
        self.example_admin_password = get_random_string(10)

        user = User.objects.create(
            username=self.example_user
        )
        user.set_password(self.example_user_password)
        user.save()

        admin = User.objects.create_superuser(
            username=self.example_admin
        )
        admin.set_password(self.example_admin_password)
        admin.save()

        self.client = Client()

    def assertNavbar(self, response):
        self.assertContains(response, "Home")
        self.assertContains(response, "Add File")
        self.assertContains(response, "Add Directory")
        self.assertContains(response, "Delete File")
        self.assertContains(response, "Delete Directory")

    def assertNavbarLogout(self, response):
        self.assertContains(response, "Login")
        self.assertNavbar(response)

    def assertNavbarUser(self, response):
        self.assertContains(response, self.example_user)
        self.assertContains(response, "Logout")
        self.assertNavbar(response)

    def assertNavbarAdmin(self, response):
        self.assertContains(response, self.example_admin)
        self.assertContains(response, "Logout")
        self.assertContains(response, "Create User")
        self.assertNavbar(response)


class IndexViewTest(TestCaseRandomApp):
    def test_logout_navbar(self):
        response = self.client.get(self.url)
        self.assertNavbarLogout(response)

    def test_user_navbar(self):
        self.login_as_user()
        response = self.client.get(self.url)
        self.assertNavbarUser(response)

    def test_admin_navbar(self):
        self.login_as_admin()
        response = self.client.get(self.url)
        self.assertNavbarAdmin(response)

    def test_random(self):
        self.test_logout_navbar()

        for i in range(random.randint(10, 50)):
            if random.randint(0, 1) == 0:
                self.test_admin_navbar()
            else:
                self.test_user_navbar()
            self.logout()
            self.test_logout_navbar()


class FilesViewTest(TestCaseRandomApp):
    def test_files_view(self):
        file_name = get_random_string(10)

        models.File.objects.create(
            owner=User.objects.get(username=self.example_user),
            name=file_name,
            description=get_random_string(20),
            parent=None
        )

        self.login_as_user()
        response = self.client.get(self.url)
        self.assertContains(response, file_name)

    def test_add_file_view(self):
        file_name = get_random_string(10)
        file = SimpleUploadedFile(
            f"{get_random_string(10)}.c",
            str.encode(simple_framac_program)
        )

        data = {
            "name": file_name,
            "description": get_random_string(20),
            "content": file
        }

        self.login_as_user()
        response = self.client.post(reverse("file-add"), data, follow=True)
        self.assertContains(response, file_name)
        self.assertNavbarUser(response)

    def test_delete_file_view(self):
        file_name = get_random_string(10)

        file = models.File.objects.create(
            owner=User.objects.get(username=self.example_user),
            name=file_name,
            description=get_random_string(20),
            parent=None
        )

        self.login_as_user()
        response = self.client.post(reverse("file-delete"), {
            "file": file.pk
        }, follow=True)
        self.assertNotContains(response, file_name)
        self.assertFalse(models.File.objects.get(
            pk=file.pk
        ).validity)


class DirectoryViewTest(TestCaseRandomApp):
    def test_directory_view(self):
        directory_name = get_random_string(10)

        models.Directory.objects.create(
            owner=User.objects.get(username=self.example_user),
            name=directory_name,
            description=get_random_string(20),
            parent=None
        )

        self.login_as_user()
        response = self.client.get(self.url)
        self.assertContains(response, directory_name)

    def test_add_directory_view(self):
        directory_name = get_random_string(10)

        self.login_as_user()
        response = self.client.post(reverse("directory-add"), {
            "name": directory_name,
            "description": get_random_string(20),
        }, follow=True)
        self.assertContains(response, directory_name)

    def test_delete_directory_view(self):
        directory_name = get_random_string(10)

        directory = models.Directory.objects.create(
            owner=User.objects.get(username=self.example_user),
            name=directory_name,
            description=get_random_string(20),
            parent=None
        )

        self.login_as_user()
        response = self.client.post(reverse("directory-delete"), {
            "directory": directory.pk
        }, follow=True)
        self.assertNotContains(response, directory_name)
        self.assertFalse(models.Directory.objects.get(
            pk=directory.pk
        ).validity)


class UserFileSystemViewTest(TestCaseRandomApp):
    def test_see_others_stuff(self):
        directory_name = get_random_string(10)

        directory = models.Directory.objects.create(
            owner=User.objects.get(username=self.example_admin),
            name=directory_name,
            description=get_random_string(20),
            parent=None
        )

        file_name = get_random_string(10)

        models.File.objects.create(
            owner=User.objects.get(username=self.example_admin),
            name=file_name,
            description=get_random_string(20),
            parent=directory
        )

        self.login_as_user()
        response = self.client.get(self.url)
        self.assertNotContains(response, directory_name)
        self.assertNotContains(response, file_name)


class FileGetViewTest(TestCaseRandomApp):
    def test_other_user_code(self):
        file = models.File.objects.create(
            owner=User.objects.get(username=self.example_admin),
            name=get_random_string(10),
            description=get_random_string(20),
        )

        self.login_as_user()
        response = self.client.get(reverse("file-get", kwargs={"file_pk": file.pk}))
        self.assertEquals(response.status_code, 403)

    def test_code(self):
        file_content = get_random_string(100)

        file = models.File.objects.create(
            owner=User.objects.get(username=self.example_user),
            name=get_random_string(10),
            description=get_random_string(20),
            content=SimpleUploadedFile(
                "test",
                str.encode(file_content)
            )
        )

        self.login_as_user()
        response = self.client.get(reverse("file-get", kwargs={"file_pk": file.pk}))
        self.assertEquals(response.json()['code'], file_content)


simple_framac_program = """/*@ predicate sorted{L}(long *t, integer a, integer b) =
  @    \\forall integer i,j; a <= i <= j <= b ==> t[i] <= t[j];
  @*/

/*@ requires n >= 0 && \\valid_range(t,0,n-1);
  @ ensures -1 <= \\result < n;
  @ behavior success:
  @   ensures \\result >= 0 ==> t[\\result] == v;
  @ behavior failure:
  @   assumes sorted(t,0,n-1);
  @   ensures \\result == -1 ==>
  @     \\forall integer k; 0 <= k < n ==> t[k] != v;
  @*/
int binary_search(long t[], int n, long v) {
  int l = 0, u = n-1;
  /*@ loop invariant
    @   0 <= l && u <= n-1;
    @ for failure:
    @   loop invariant
    @   \\forall integer k; 0 <= k < n && t[k] == v ==> l <= k <= u;
    @ loop variant u-l;
    @*/
  while (l <= u ) {
    int m = (l + u) / 2;
    //@ assert l <= m <= u;
    if (t[m] < v) l = m + 1;
    else if (t[m] > v) u = m - 1;
    else return m;
  }
  return -1;
}"""