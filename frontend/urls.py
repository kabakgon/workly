from django.urls import path
from . import views

app_name = 'frontend'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.dashboard, name='dashboard'),
    path('projects/', views.projects_list, name='projects_list'),
    path('projects/<int:pk>/', views.project_detail, name='project_detail'),
    path('projects/<int:pk>/gantt/', views.project_gantt, name='project_gantt'),
    path('tasks/', views.tasks_list, name='tasks_list'),
]

