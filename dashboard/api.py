from django.db.models import Q, Count
from rest_framework import generics, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView
from rest_framework.response import Response

from projects.models import Project
from tasks.models import Task
from projects.serializers import ProjectSerializer
from tasks.serializers import TaskSerializer


class MyProjectsList(generics.ListAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        u = self.request.user
        return (
            Project.objects.filter(Q(owner=u) | Q(tasks__assignee=u))
            .distinct()
            .order_by("-updated_at", "-created_at")
        )


class MyTasksList(generics.ListAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["status", "project"]
    search_fields = ["title", "description"]
    ordering_fields = [
        "start_date",
        "end_date",
        "progress",
        "sort_index",
        "id",
        "created_at",
    ]
    ordering = ["start_date", "sort_index", "id"]

    def get_queryset(self):
        u = self.request.user
        return Task.objects.filter(assignee=u).select_related(
            "project", "parent", "assignee"
        )


class DashboardSummary(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        u = request.user
        my_projects_qs = Project.objects.filter(
            Q(owner=u) | Q(tasks__assignee=u)
        ).distinct()
        my_tasks_qs = Task.objects.filter(assignee=u)

        by_status = list(
            my_tasks_qs.values("status").annotate(count=Count("id")).order_by("status")
        )
        next_task = (
            my_tasks_qs.exclude(start_date__isnull=True)
            .order_by("start_date")
            .values("id", "title", "project_id", "start_date", "end_date")
            .first()
        )

        return Response(
            {
                "my_projects_count": my_projects_qs.count(),
                "my_tasks_count": my_tasks_qs.count(),
                "my_tasks_by_status": by_status,
                "next_task": next_task,
            }
        )
