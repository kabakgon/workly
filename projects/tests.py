"""
Tests for Projects API endpoints.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from datetime import date, timedelta
from .models import Project

User = get_user_model()


class ProjectAPITestCase(TestCase):
    """Test cases for Project API endpoints."""

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
        self.client.force_authenticate(user=self.user)

    def test_list_projects(self):
        """Test listing all projects."""
        # Create test projects
        project1 = Project.objects.create(
            name='Test Project 1',
            description='Description 1',
            status='active',
            priority=2,
            owner=self.user
        )
        project2 = Project.objects.create(
            name='Test Project 2',
            description='Description 2',
            status='planned',
            priority=3,
            owner=self.other_user
        )

        response = self.client.get('/api/projects/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_create_project(self):
        """Test creating a new project."""
        data = {
            'name': 'New Project',
            'description': 'New project description',
            'start_date': date.today().isoformat(),
            'end_date': (date.today() + timedelta(days=30)).isoformat(),
            'status': 'active',
            'priority': 2,
            'owner': self.user.id
        }
        response = self.client.post('/api/projects/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Project.objects.count(), 1)
        self.assertEqual(Project.objects.get().name, 'New Project')
        self.assertEqual(Project.objects.get().owner, self.user)

    def test_create_project_required_fields(self):
        """Test that required fields are validated."""
        data = {
            'description': 'Missing name'
        }
        response = self.client.post('/api/projects/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_project(self):
        """Test retrieving a single project."""
        project = Project.objects.create(
            name='Test Project',
            description='Test description',
            status='active',
            priority=2,
            owner=self.user
        )
        response = self.client.get(f'/api/projects/{project.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Project')
        self.assertEqual(response.data['owner'], self.user.id)

    def test_update_project_as_owner(self):
        """Test updating a project as the owner."""
        project = Project.objects.create(
            name='Test Project',
            description='Original description',
            status='active',
            priority=2,
            owner=self.user
        )
        data = {
            'name': 'Updated Project',
            'description': 'Updated description',
            'status': 'active',
            'priority': 3,
            'owner': self.user.id
        }
        response = self.client.put(f'/api/projects/{project.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        project.refresh_from_db()
        self.assertEqual(project.name, 'Updated Project')
        self.assertEqual(project.priority, 3)

    def test_update_project_as_non_owner(self):
        """Test that non-owners cannot update projects."""
        project = Project.objects.create(
            name='Test Project',
            description='Test description',
            status='active',
            priority=2,
            owner=self.other_user
        )
        data = {
            'name': 'Hacked Project',
            'description': 'Hacked description',
            'status': 'active',
            'priority': 2,
            'owner': self.other_user.id
        }
        response = self.client.put(f'/api/projects/{project.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_partial_update_project(self):
        """Test partial update (PATCH) of a project."""
        project = Project.objects.create(
            name='Test Project',
            description='Original description',
            status='active',
            priority=2,
            owner=self.user
        )
        data = {'name': 'Partially Updated Project'}
        response = self.client.patch(f'/api/projects/{project.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        project.refresh_from_db()
        self.assertEqual(project.name, 'Partially Updated Project')
        self.assertEqual(project.description, 'Original description')

    def test_delete_project(self):
        """Test deleting a project."""
        project = Project.objects.create(
            name='Test Project',
            description='Test description',
            status='active',
            priority=2,
            owner=self.user
        )
        response = self.client.delete(f'/api/projects/{project.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Project.objects.count(), 0)

    def test_delete_project_with_tasks(self):
        """Test that deleting a project with tasks returns 409."""
        from tasks.models import Task
        project = Project.objects.create(
            name='Test Project',
            description='Test description',
            status='active',
            priority=2,
            owner=self.user
        )
        Task.objects.create(
            project=project,
            title='Test Task',
            status='todo'
        )
        response = self.client.delete(f'/api/projects/{project.id}/')
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertIn('zadania', response.data['detail'].lower())

    def test_filter_projects_by_status(self):
        """Test filtering projects by status."""
        Project.objects.create(
            name='Active Project',
            status='active',
            priority=2,
            owner=self.user
        )
        Project.objects.create(
            name='Planned Project',
            status='planned',
            priority=2,
            owner=self.user
        )
        response = self.client.get('/api/projects/?status=active')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['status'], 'active')

    def test_filter_projects_by_owner(self):
        """Test filtering projects by owner."""
        Project.objects.create(
            name='My Project',
            status='active',
            priority=2,
            owner=self.user
        )
        Project.objects.create(
            name='Other Project',
            status='active',
            priority=2,
            owner=self.other_user
        )
        response = self.client.get(f'/api/projects/?owner={self.user.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['owner'], self.user.id)

    def test_search_projects(self):
        """Test searching projects by name and description."""
        Project.objects.create(
            name='Python Project',
            description='Django development',
            status='active',
            priority=2,
            owner=self.user
        )
        Project.objects.create(
            name='JavaScript Project',
            description='React development',
            status='active',
            priority=2,
            owner=self.user
        )
        response = self.client.get('/api/projects/?search=Python')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Python Project')

    def test_ordering_projects(self):
        """Test ordering projects."""
        project1 = Project.objects.create(
            name='A Project',
            status='active',
            priority=2,
            owner=self.user
        )
        project2 = Project.objects.create(
            name='B Project',
            status='active',
            priority=2,
            owner=self.user
        )
        response = self.client.get('/api/projects/?ordering=name')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['name'], 'A Project')
        self.assertEqual(response.data['results'][1]['name'], 'B Project')

    def test_unauthenticated_access(self):
        """Test that unauthenticated users cannot access projects."""
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/projects/')
        # IsProjectOwnerOrReadOnly requires authentication, returns 403
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_tasks_count_field(self):
        """Test that tasks_count is included in project serializer."""
        from tasks.models import Task
        project = Project.objects.create(
            name='Test Project',
            status='active',
            priority=2,
            owner=self.user
        )
        Task.objects.create(
            project=project,
            title='Task 1',
            status='todo'
        )
        Task.objects.create(
            project=project,
            title='Task 2',
            status='todo'
        )
        response = self.client.get(f'/api/projects/{project.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['tasks_count'], 2)
