from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import status
from django.shortcuts import get_object_or_404

from projects.models import Project
from tasks.models import Task, Dependency


class GanttProjectView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, pk: int):
        project = get_object_or_404(Project, pk=pk)

        tasks = (
            Task.objects.filter(project=project)
            .select_related("parent", "assignee")
            .order_by("sort_index", "id")
        )
        deps = Dependency.objects.filter(successor__project=project)

        data = [
            {
                "id": t.id,
                "text": t.title,
                "start_date": t.start_date.isoformat() if t.start_date else None,
                "end_date": t.end_date.isoformat() if t.end_date else None,
                "progress": (t.progress or 0) / 100.0,
                "parent": t.parent_id,
                "status": t.status,
            }
            for t in tasks
        ]

        links = [
            {
                "id": d.id,
                "source": d.predecessor_id,
                "target": d.successor_id,
                "type": d.type,  # FS/SS/FF/SF
                "lag": d.lag_days,
            }
            for d in deps
        ]

        return Response({"data": data, "links": links})
