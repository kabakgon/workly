from django.contrib import admin
from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "project",
        "status",
        "start_date",
        "end_date",
        "progress",
        "parent",
        "sort_index",
    )
    list_filter = ("project", "status", "assignee")
    search_fields = ("title", "description")
    autocomplete_fields = ("project", "parent", "assignee")
    ordering = ("project", "sort_index", "id")
