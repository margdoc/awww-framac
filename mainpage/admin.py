from django.contrib import admin

from .models import Directory, File, StatusData, FileSection

admin.site.register(Directory)
admin.site.register(File)
admin.site.register(StatusData)
admin.site.register(FileSection)
