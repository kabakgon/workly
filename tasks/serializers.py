from rest_framework import serializers
from .models import Task, Dependency


class TaskSerializer(serializers.ModelSerializer):
    duration_days = serializers.ReadOnlyField()

    class Meta:
        model = Task
        fields = [
            "id",
            "project",
            "parent",
            "title",
            "description",
            "assignee",
            "status",
            "start_date",
            "end_date",
            "progress",
            "sort_index",
            "estimated_hours",
            "actual_hours",
            "duration_days",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at", "duration_days"]


class DependencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Dependency
        fields = [
            "id",
            "predecessor",
            "successor",
            "type",
            "lag_days",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]
