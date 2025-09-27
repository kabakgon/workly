from django.contrib import admin
from .models import Task, Dependency


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


@admin.register(Dependency)
class DependencyAdmin(admin.ModelAdmin):
    list_display = ("predecessor", "type", "successor", "lag_days")
    list_filter = ("type",)
    search_fields = ("predecessor__title", "successor__title")
    autocomplete_fields = ("predecessor", "successor")
