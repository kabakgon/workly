from rest_framework import serializers
from .models import Project


class ProjectSerializer(serializers.ModelSerializer):
    tasks_count = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "description",
            "start_date",
            "end_date",
            "status",
            "priority",
            "owner",
            "created_at",
            "updated_at",
            "tasks_count",
        ]
        read_only_fields = ["created_at", "updated_at", "tasks_count"]

    def get_tasks_count(self, obj):
        return obj.tasks.count()
