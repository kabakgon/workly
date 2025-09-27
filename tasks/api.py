from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Task, Dependency
from .serializers import TaskSerializer, DependencySerializer


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.select_related("project", "assignee", "parent").all()
    serializer_class = TaskSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["project", "status", "assignee", "parent"]
    search_fields = ["title", "description"]
    ordering_fields = [
        "sort_index",
        "start_date",
        "end_date",
        "progress",
        "id",
        "title",
    ]
    ordering = ["project", "sort_index", "id"]


class DependencyViewSet(viewsets.ModelViewSet):
    queryset = Dependency.objects.select_related("predecessor", "successor").all()
    serializer_class = DependencySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["predecessor", "successor", "type"]
