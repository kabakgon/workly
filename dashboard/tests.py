"""
Tests for Dashboard API endpoints.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from datetime import date, timedelta
from projects.models import Project
from tasks.models import Task

User = get_user_model()


class DashboardAPITestCase(TestCase):
    """Test cases for Dashboard API endpoints."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        self.project = Project.objects.create(
            name='My Project',
            description='My project description',
            status='active',
            priority=2,
            owner=self.user
        )
        self.other_project = Project.objects.create(
            name='Other Project',
            description='Other project description',
            status='active',
            priority=2,
            owner=self.other_user
        )
        self.client.force_authenticate(user=self.user)

    def test_my_projects_list(self):
        """Test listing user's projects."""
        # Create tasks assigned to user in owned project
        Task.objects.create(
            project=self.project,
            title='My Task',
            status='todo',
            assignee=self.user
        )
        # Create task assigned to user in other project
        Task.objects.create(
            project=self.other_project,
            title='My Task in Other Project',
            status='todo',
            assignee=self.user
        )
        response = self.client.get('/api/my/projects/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # MyProjectsList uses ListAPIView, so it's paginated
        self.assertIn('results', response.data)
        # Should include both: owned project and project with assigned tasks
        self.assertEqual(len(response.data['results']), 2)

    def test_my_tasks_list(self):
        """Test listing user's tasks."""
        Task.objects.create(
            project=self.project,
            title='My Task 1',
            status='todo',
            assignee=self.user
        )
        Task.objects.create(
            project=self.project,
            title='My Task 2',
            status='in_progress',
            assignee=self.user
        )
        Task.objects.create(
            project=self.other_project,
            title='Other Task',
            status='todo',
            assignee=self.other_user
        )
        response = self.client.get('/api/my/tasks/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # MyTasksList uses ListAPIView, so it's paginated
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 2)

    def test_my_tasks_filter_by_status(self):
        """Test filtering user's tasks by status."""
        Task.objects.create(
            project=self.project,
            title='Todo Task',
            status='todo',
            assignee=self.user
        )
        Task.objects.create(
            project=self.project,
            title='Done Task',
            status='done',
            assignee=self.user
        )
        response = self.client.get('/api/my/tasks/?status=todo')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # MyTasksList uses ListAPIView, so it's paginated
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['status'], 'todo')

    def test_my_tasks_filter_by_project(self):
        """Test filtering user's tasks by project."""
        Task.objects.create(
            project=self.project,
            title='Task in Project 1',
            status='todo',
            assignee=self.user
        )
        Task.objects.create(
            project=self.other_project,
            title='Task in Project 2',
            status='todo',
            assignee=self.user
        )
        response = self.client.get(f'/api/my/tasks/?project={self.project.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # MyTasksList uses ListAPIView, so it's paginated
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['project'], self.project.id)

    def test_dashboard_summary(self):
        """Test dashboard summary endpoint."""
        Task.objects.create(
            project=self.project,
            title='Todo Task',
            status='todo',
            assignee=self.user
        )
        Task.objects.create(
            project=self.project,
            title='In Progress Task',
            status='in_progress',
            assignee=self.user
        )
        Task.objects.create(
            project=self.project,
            title='Done Task',
            status='done',
            assignee=self.user
        )
        response = self.client.get('/api/my/summary/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['my_projects_count'], 1)
        self.assertEqual(response.data['my_tasks_count'], 3)
        self.assertIn('my_tasks_by_status', response.data)
        self.assertIn('next_task', response.data)

    def test_dashboard_summary_tasks_by_status(self):
        """Test that dashboard summary includes tasks grouped by status."""
        Task.objects.create(
            project=self.project,
            title='Todo Task',
            status='todo',
            assignee=self.user
        )
        Task.objects.create(
            project=self.project,
            title='Another Todo Task',
            status='todo',
            assignee=self.user
        )
        Task.objects.create(
            project=self.project,
            title='Done Task',
            status='done',
            assignee=self.user
        )
        response = self.client.get('/api/my/summary/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        status_counts = {s['status']: s['count'] for s in response.data['my_tasks_by_status']}
        self.assertEqual(status_counts.get('todo', 0), 2)
        self.assertEqual(status_counts.get('done', 0), 1)

    def test_dashboard_summary_next_task(self):
        """Test that dashboard summary includes next task."""
        today = date.today()
        Task.objects.create(
            project=self.project,
            title='Past Task',
            status='todo',
            assignee=self.user,
            start_date=today - timedelta(days=5)
        )
        Task.objects.create(
            project=self.project,
            title='Future Task',
            status='todo',
            assignee=self.user,
            start_date=today + timedelta(days=5)
        )
        Task.objects.create(
            project=self.project,
            title='Today Task',
            status='todo',
            assignee=self.user,
            start_date=today
        )
        response = self.client.get('/api/my/summary/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data['next_task'])
        # Should be the earliest task (past task)
        self.assertEqual(response.data['next_task']['title'], 'Past Task')

    def test_my_timeline_view(self):
        """Test timeline view endpoint."""
        today = date.today()
        Task.objects.create(
            project=self.project,
            title='Task 1',
            status='todo',
            assignee=self.user,
            start_date=today,
            end_date=today + timedelta(days=5)
        )
        Task.objects.create(
            project=self.project,
            title='Task 2',
            status='in_progress',
            assignee=self.user,
            start_date=today + timedelta(days=10),
            end_date=today + timedelta(days=15)
        )
        response = self.client.get('/api/my/timeline/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('window', response.data)
        self.assertIn('data', response.data)
        self.assertEqual(len(response.data['data']), 2)

    def test_my_timeline_view_with_days_parameter(self):
        """Test timeline view with custom days parameter."""
        today = date.today()
        Task.objects.create(
            project=self.project,
            title='Task in Window',
            status='todo',
            assignee=self.user,
            start_date=today,
            end_date=today + timedelta(days=5)
        )
        Task.objects.create(
            project=self.project,
            title='Task Outside Window',
            status='todo',
            assignee=self.user,
            start_date=today + timedelta(days=30),
            end_date=today + timedelta(days=35)
        )
        response = self.client.get('/api/my/timeline/?days=14')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Only task within 14 days should be included
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['text'], 'Task in Window')

    def test_my_timeline_view_with_from_parameter(self):
        """Test timeline view with custom from date parameter."""
        today = date.today()
        future_date = today + timedelta(days=10)
        Task.objects.create(
            project=self.project,
            title='Future Task',
            status='todo',
            assignee=self.user,
            start_date=future_date,
            end_date=future_date + timedelta(days=5)
        )
        response = self.client.get(f'/api/my/timeline/?from={future_date.isoformat()}&days=14')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['text'], 'Future Task')

    def test_users_list_view(self):
        """Test users list endpoint."""
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # UsersListView returns a list directly, not paginated
        self.assertEqual(len(response.data), 2)  # testuser and otheruser
        usernames = [user['username'] for user in response.data]
        self.assertIn('testuser', usernames)
        self.assertIn('otheruser', usernames)

    def test_users_list_view_fields(self):
        """Test that users list includes correct fields."""
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # UsersListView returns a list directly
        self.assertIsInstance(response.data, list)
        user = response.data[0]
        self.assertIn('id', user)
        self.assertIn('username', user)
        self.assertIn('email', user)

    def test_unauthenticated_access(self):
        """Test that unauthenticated users cannot access dashboard endpoints."""
        self.client.force_authenticate(user=None)
        endpoints = [
            '/api/my/projects/',
            '/api/my/tasks/',
            '/api/my/summary/',
            '/api/my/timeline/',
            '/api/users/'
        ]
        for endpoint in endpoints:
            response = self.client.get(endpoint)
            # IsAuthenticated returns 403 for unauthenticated users
            self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
                         f"Endpoint {endpoint} should require authentication")
