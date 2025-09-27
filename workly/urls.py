from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from projects.api import ProjectViewSet
from tasks.api import TaskViewSet, DependencyViewSet
from gantt.api import GanttProjectView

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView


router = DefaultRouter()
router.register(r"projects", ProjectViewSet, basename="project")
router.register(r"tasks", TaskViewSet, basename="task")
router.register(r"dependencies", DependencyViewSet, basename="dependency")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path(
        "api/projects/<int:pk>/gantt/", GanttProjectView.as_view(), name="project-gantt"
    ),
    path("api/", include(("dashboard.urls", "dashboard"), namespace="dashboard")),
]

urlpatterns += [
    # OpenAPI schema (JSON/YAML)
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    # Swagger UI
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="docs"),
    # Redoc (alternatywna dokumentacja)
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]
