from django.urls import path
from .api import MyProjectsList, MyTasksList, DashboardSummary, MyTimelineView, UsersListView

app_name = "dashboard"

urlpatterns = [
    path("my/projects/", MyProjectsList.as_view(), name="my-projects"),
    path("my/tasks/", MyTasksList.as_view(), name="my-tasks"),
    path("my/summary/", DashboardSummary.as_view(), name="summary"),
    path("my/timeline/", MyTimelineView.as_view(), name="my-timeline"),
    path("users/", UsersListView.as_view(), name="users-list"),
]
