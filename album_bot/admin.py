from django.contrib import admin
from .models import Album, Image


class ImageInline(admin.TabularInline):
    model = Image


@admin.register(Album)
class SubjectAdmin(admin.ModelAdmin):
    inlines = [ImageInline]

