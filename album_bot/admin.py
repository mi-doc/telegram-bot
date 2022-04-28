from django.contrib import admin
from .models import Subject, Image


class ImageInline(admin.TabularInline):
    model = Image


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    inlines = [ImageInline]

