from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('file/<int:file_pk>', views.file_get_endpoint, name='file-get'),
    path('file/<int:file_pk>/change', views.file_change, name='file-change'),
    path('file/<int:file_pk>/rerun', views.file_rerun, name='file-rerun'),
    path('file/add', views.file_add, name='file-add'),
    path('file/delete', views.file_delete, name='file-delete'),
    path('directory/add', views.directory_add, name='directory-add'),
    path('directory/delete', views.directory_delete, name='directory-delete'),
]