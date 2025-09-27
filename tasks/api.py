from django.db import transaction
from django.db.models import Max
from django.db.models.deletion import ProtectedError
from django_filters.rest_framework import DjangoFilterBackend
from projects.models import Project
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Dependency, Task
from .serializers import DependencySerializer, TaskSerializer
from .permissions import IsAssigneeOrProjectOwnerOrReadOnly


class TaskViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAssigneeOrProjectOwnerOrReadOnly]
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

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError:
            return Response(
                {
                    "detail": "Nie można usunąć zadania, które jest powiązane zależnościami."
                },
                status=status.HTTP_409_CONFLICT,
            )

    @action(detail=True, methods=["post"])
    def copy(self, request, pk=None):
        src = self.get_object()
        include_children = bool(request.data.get("include_children", False))

        # opcjonalne nadpisanie projektu/rodzica i tytułu
        target_project_id = request.data.get("project")  # int
        target_parent_id = request.data.get("parent")  # int
        new_title = request.data.get("title")  # str

        target_project = src.project
        if target_project_id:
            target_project = Project.objects.get(pk=target_project_id)

        target_parent = None
        if target_parent_id:
            target_parent = Task.objects.get(pk=target_parent_id)

        @transaction.atomic
        def perform_copy():
            def next_sort_index(project):
                return (
                    Task.objects.filter(project=project).aggregate(Max("sort_index"))[
                        "sort_index__max"
                    ]
                    or 0
                ) + 10

            def clone_one(source_task, parent_override, project_override, root=False):
                title = new_title if (root and new_title) else source_task.title
                clone = Task.objects.create(
                    project=project_override,
                    parent=parent_override,
                    title=(
                        title
                        if not root
                        else (new_title or f"Kopia: {source_task.title}")
                    ),
                    description=source_task.description,
                    assignee=source_task.assignee,
                    status=source_task.status,
                    start_date=source_task.start_date,
                    end_date=source_task.end_date,
                    progress=source_task.progress,
                    sort_index=next_sort_index(project_override),
                    estimated_hours=source_task.estimated_hours,
                    actual_hours=None,  # reset metryk wykonania
                )
                return clone

            # korzeń
            new_root = clone_one(src, target_parent, target_project, root=True)

            # rekurencyjnie dzieci (jeśli trzeba)
            if include_children:

                def clone_children(src_parent, dst_parent):
                    for ch in src_parent.children.all().order_by("sort_index", "id"):
                        ch_clone = clone_one(ch, dst_parent, target_project)
                        clone_children(ch, ch_clone)

                clone_children(src, new_root)
            return new_root

        new_task = perform_copy()
        serializer = self.get_serializer(new_task)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class DependencyViewSet(viewsets.ModelViewSet):
    queryset = Dependency.objects.select_related("from_task", "to_task").all()
    serializer_class = DependencySerializer

    def get_permissions(self):
        from projects.permissions import IsProjectOwnerOrReadOnly

        return [IsProjectOwnerOrReadOnly()]
