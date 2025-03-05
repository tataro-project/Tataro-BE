from django.contrib import admin

from helpers.models import Category

from .models import Notice


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):  # type: ignore
    list_display = ("name", "description")
    search_fields = ("name",)


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):  # type: ignore
    list_display = ("title", "category", "user", "created_at")
    list_filter = ("category",)
    search_fields = ("title", "content")
