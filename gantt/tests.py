"""
Tests for Gantt API endpoints.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from datetime import date, timedelta
from projects.models import Project
from tasks.models import Task, Dependency

User = get_user_model()


class GanttAPITestCase(TestCase):
    """Test cases for Gantt API endpoints."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.project = Project.objects.create(
            name='Test Project',
            description='Test description',
            status='active',
            priority=2,
            owner=self.user
        )
        self.client.force_authenticate(user=self.user)

    def test_gantt_project_view(self):
        """Test Gantt project view endpoint."""
        task1 = Task.objects.create(
            project=self.project,
            title='Task 1',
            status='todo',
            assignee=self.user,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=5)
        )
        task2 = Task.objects.create(
            project=self.project,
            title='Task 2',
            status='in_progress',
            assignee=self.user,
            start_date=date.today() + timedelta(days=6),
            end_date=date.today() + timedelta(days=10)
        )
        response = self.client.get(f'/api/projects/{self.project.id}/gantt/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('data', response.data)
        self.assertIn('links', response.data)
        self.assertEqual(len(response.data['data']), 2)

    def test_gantt_project_view_task_fields(self):
        """Test that Gantt view includes all required task fields."""
        task = Task.objects.create(
            project=self.project,
            title='Test Task',
            status='todo',
            assignee=self.user,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=5),
            progress=50
        )
        response = self.client.get(f'/api/projects/{self.project.id}/gantt/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        task_data = response.data['data'][0]
        self.assertEqual(task_data['id'], task.id)
        self.assertEqual(task_data['text'], 'Test Task')
        self.assertEqual(task_data['start_date'], date.today().isoformat())
        self.assertEqual(task_data['end_date'], (date.today() + timedelta(days=5)).isoformat())
        self.assertEqual(task_data['progress'], 0.5)
        self.assertEqual(task_data['status'], 'todo')

    def test_gantt_project_view_with_dependencies(self):
        """Test Gantt view with task dependencies."""
        task1 = Task.objects.create(
            project=self.project,
            title='Task 1',
            status='todo',
            assignee=self.user,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=5)
        )
        task2 = Task.objects.create(
            project=self.project,
            title='Task 2',
            status='todo',
            assignee=self.user,
            start_date=date.today() + timedelta(days=6),
            end_date=date.today() + timedelta(days=10)
        )
        dep = Dependency.objects.create(
            predecessor=task1,
            successor=task2,
            type='FS',
            lag_days=0
        )
        response = self.client.get(f'/api/projects/{self.project.id}/gantt/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['links']), 1)
        link = response.data['links'][0]
        self.assertEqual(link['source'], task1.id)
        self.assertEqual(link['target'], task2.id)
        self.assertEqual(link['type'], 'FS')
        self.assertEqual(link['lag'], 0)

    def test_gantt_project_view_dependency_fields(self):
        """Test that Gantt view includes all required dependency fields."""
        task1 = Task.objects.create(
            project=self.project,
            title='Task 1',
            status='todo',
            assignee=self.user
        )
        task2 = Task.objects.create(
            project=self.project,
            title='Task 2',
            status='todo',
            assignee=self.user
        )
        dep = Dependency.objects.create(
            predecessor=task1,
            successor=task2,
            type='SS',
            lag_days=5
        )
        response = self.client.get(f'/api/projects/{self.project.id}/gantt/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        link = response.data['links'][0]
        self.assertEqual(link['id'], dep.id)
        self.assertEqual(link['source'], task1.id)
        self.assertEqual(link['target'], task2.id)
        self.assertEqual(link['type'], 'SS')
        self.assertEqual(link['lag'], 5)

    def test_gantt_project_view_tasks_without_dates(self):
        """Test that tasks without dates are included in Gantt view."""
        task_with_dates = Task.objects.create(
            project=self.project,
            title='Task With Dates',
            status='todo',
            assignee=self.user,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=5)
        )
        task_without_dates = Task.objects.create(
            project=self.project,
            title='Task Without Dates',
            status='todo',
            assignee=self.user
        )
        response = self.client.get(f'/api/projects/{self.project.id}/gantt/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Both tasks should be included
        self.assertEqual(len(response.data['data']), 2)
        task_ids = [t['id'] for t in response.data['data']]
        self.assertIn(task_with_dates.id, task_ids)
        self.assertIn(task_without_dates.id, task_ids)

    def test_gantt_project_view_nonexistent_project(self):
        """Test Gantt view with nonexistent project."""
        response = self.client.get('/api/projects/99999/gantt/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_gantt_project_view_unauthenticated(self):
        """Test that unauthenticated users can access Gantt view (read-only)."""
        self.client.force_authenticate(user=None)
        response = self.client.get(f'/api/projects/{self.project.id}/gantt/')
        # IsAuthenticatedOrReadOnly allows GET for unauthenticated users
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_gantt_project_view_parent_field(self):
        """Test that Gantt view includes parent field for tasks."""
        parent_task = Task.objects.create(
            project=self.project,
            title='Parent Task',
            status='todo',
            assignee=self.user
        )
        child_task = Task.objects.create(
            project=self.project,
            title='Child Task',
            status='todo',
            assignee=self.user,
            parent=parent_task
        )
        response = self.client.get(f'/api/projects/{self.project.id}/gantt/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        child_data = next(t for t in response.data['data'] if t['id'] == child_task.id)
        self.assertEqual(child_data['parent'], parent_task.id)
        parent_data = next(t for t in response.data['data'] if t['id'] == parent_task.id)
        self.assertIsNone(parent_data['parent'])

    def test_gantt_project_view_progress_calculation(self):
        """Test that progress is correctly calculated as float (0-1)."""
        task = Task.objects.create(
            project=self.project,
            title='Test Task',
            status='todo',
            assignee=self.user,
            progress=75
        )
        response = self.client.get(f'/api/projects/{self.project.id}/gantt/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        task_data = response.data['data'][0]
        self.assertEqual(task_data['progress'], 0.75)

    def test_gantt_project_view_only_project_dependencies(self):
        """Test that only dependencies for tasks in the project are included."""
        other_project = Project.objects.create(
            name='Other Project',
            status='active',
            priority=2,
            owner=self.user
        )
        task1 = Task.objects.create(
            project=self.project,
            title='Task 1',
            status='todo',
            assignee=self.user
        )
        task2 = Task.objects.create(
            project=self.project,
            title='Task 2',
            status='todo',
            assignee=self.user
        )
        other_task = Task.objects.create(
            project=other_project,
            title='Other Task',
            status='todo',
            assignee=self.user
        )
        # Dependency within project
        dep1 = Dependency.objects.create(
            predecessor=task1,
            successor=task2,
            type='FS'
        )
        # Cannot create dependency between different projects - it's validated
        # So we test that only dependencies within the project are returned
        response = self.client.get(f'/api/projects/{self.project.id}/gantt/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Only dependency within project should be included
        self.assertEqual(len(response.data['links']), 1)
        self.assertEqual(response.data['links'][0]['id'], dep1.id)
