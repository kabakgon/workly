from rest_framework import viewsets, filters, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from django.db.models.deletion import ProtectedError
from .models import Project
from .serializers import ProjectSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["status", "priority", "owner"]
    search_fields = ["name", "description"]
    ordering_fields = [
        "created_at",
        "updated_at",
        "priority",
        "start_date",
        "end_date",
        "name",
    ]
    ordering = ["-created_at"]

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError:
            return Response(
                {"detail": "Nie można usunąć projektu, który ma przypięte zadania."},
                status=status.HTTP_409_CONFLICT,
            )
