from django.contrib import admin

from django.contrib import admin
from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "status",
        "priority",
        "owner",
        "start_date",
        "end_date",
        "created_at",
    )
    list_filter = ("status", "priority", "owner")
    search_fields = ("name", "description")
    ordering = ("-created_at",)
