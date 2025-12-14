"""
Tests for Tasks API endpoints.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from datetime import date, timedelta
from projects.models import Project
from .models import Task, Dependency

User = get_user_model()


class TaskAPITestCase(TestCase):
    """Test cases for Task API endpoints."""

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
            name='Test Project',
            description='Test description',
            status='active',
            priority=2,
            owner=self.user
        )
        self.other_project = Project.objects.create(
            name='Other Project',
            description='Other description',
            status='active',
            priority=2,
            owner=self.other_user
        )
        self.client.force_authenticate(user=self.user)

    def test_list_tasks(self):
        """Test listing all tasks."""
        task1 = Task.objects.create(
            project=self.project,
            title='Task 1',
            status='todo',
            assignee=self.user
        )
        task2 = Task.objects.create(
            project=self.project,
            title='Task 2',
            status='in_progress',
            assignee=self.user
        )
        response = self.client.get('/api/tasks/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_create_task(self):
        """Test creating a new task."""
        data = {
            'project': self.project.id,
            'title': 'New Task',
            'description': 'New task description',
            'status': 'todo',
            'start_date': date.today().isoformat(),
            'end_date': (date.today() + timedelta(days=7)).isoformat(),
            'progress': 0,
            'assignee': self.user.id
        }
        response = self.client.post('/api/tasks/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 1)
        self.assertEqual(Task.objects.get().title, 'New Task')
        self.assertEqual(Task.objects.get().assignee, self.user)

    def test_create_task_required_fields(self):
        """Test that required fields are validated."""
        data = {
            'description': 'Missing title and project'
        }
        response = self.client.post('/api/tasks/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_task(self):
        """Test retrieving a single task."""
        task = Task.objects.create(
            project=self.project,
            title='Test Task',
            description='Test description',
            status='todo',
            assignee=self.user
        )
        response = self.client.get(f'/api/tasks/{task.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Task')
        self.assertEqual(response.data['assignee'], self.user.id)

    def test_update_task_as_assignee(self):
        """Test updating a task as the assignee."""
        task = Task.objects.create(
            project=self.project,
            title='Test Task',
            description='Original description',
            status='todo',
            assignee=self.user
        )
        data = {
            'project': self.project.id,
            'title': 'Updated Task',
            'description': 'Updated description',
            'status': 'in_progress',
            'progress': 50,
            'assignee': self.user.id
        }
        response = self.client.put(f'/api/tasks/{task.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        task.refresh_from_db()
        self.assertEqual(task.title, 'Updated Task')
        self.assertEqual(task.status, 'in_progress')
        self.assertEqual(task.progress, 50)

    def test_update_task_as_project_owner(self):
        """Test that project owner can update tasks."""
        task = Task.objects.create(
            project=self.project,
            title='Test Task',
            description='Test description',
            status='todo',
            assignee=self.other_user
        )
        data = {
            'project': self.project.id,
            'title': 'Updated by Owner',
            'description': 'Updated description',
            'status': 'in_progress',
            'assignee': self.other_user.id
        }
        response = self.client.put(f'/api/tasks/{task.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        task.refresh_from_db()
        self.assertEqual(task.title, 'Updated by Owner')

    def test_update_task_as_non_assignee_non_owner(self):
        """Test that non-assignees and non-owners cannot update tasks."""
        task = Task.objects.create(
            project=self.other_project,
            title='Test Task',
            description='Test description',
            status='todo',
            assignee=self.other_user
        )
        data = {
            'project': self.other_project.id,
            'title': 'Hacked Task',
            'description': 'Hacked description',
            'status': 'done',
            'assignee': self.other_user.id
        }
        response = self.client.put(f'/api/tasks/{task.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_partial_update_task(self):
        """Test partial update (PATCH) of a task."""
        task = Task.objects.create(
            project=self.project,
            title='Test Task',
            description='Original description',
            status='todo',
            assignee=self.user
        )
        data = {'status': 'in_progress', 'progress': 50}
        response = self.client.patch(f'/api/tasks/{task.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        task.refresh_from_db()
        self.assertEqual(task.status, 'in_progress')
        self.assertEqual(task.progress, 50)
        self.assertEqual(task.title, 'Test Task')

    def test_delete_task(self):
        """Test deleting a task."""
        task = Task.objects.create(
            project=self.project,
            title='Test Task',
            description='Test description',
            status='todo',
            assignee=self.user
        )
        response = self.client.delete(f'/api/tasks/{task.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Task.objects.count(), 0)

    def test_delete_task_with_dependencies(self):
        """Test that deleting a task with dependencies returns 409."""
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
        Dependency.objects.create(
            predecessor=task1,
            successor=task2,
            type='FS'
        )
        response = self.client.delete(f'/api/tasks/{task1.id}/')
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertIn('zależności', response.data['detail'].lower())

    def test_filter_tasks_by_status(self):
        """Test filtering tasks by status."""
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
        response = self.client.get('/api/tasks/?status=todo')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['status'], 'todo')

    def test_filter_tasks_by_project(self):
        """Test filtering tasks by project."""
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
        response = self.client.get(f'/api/tasks/?project={self.project.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['project'], self.project.id)

    def test_filter_tasks_by_assignee(self):
        """Test filtering tasks by assignee."""
        Task.objects.create(
            project=self.project,
            title='My Task',
            status='todo',
            assignee=self.user
        )
        Task.objects.create(
            project=self.project,
            title='Other Task',
            status='todo',
            assignee=self.other_user
        )
        response = self.client.get(f'/api/tasks/?assignee={self.user.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['assignee'], self.user.id)

    def test_search_tasks(self):
        """Test searching tasks by title and description."""
        Task.objects.create(
            project=self.project,
            title='Python Task',
            description='Django development',
            status='todo',
            assignee=self.user
        )
        Task.objects.create(
            project=self.project,
            title='JavaScript Task',
            description='React development',
            status='todo',
            assignee=self.user
        )
        response = self.client.get('/api/tasks/?search=Python')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Python Task')

    def test_copy_task(self):
        """Test copying a task."""
        task = Task.objects.create(
            project=self.project,
            title='Original Task',
            description='Original description',
            status='todo',
            assignee=self.user,
            progress=50
        )
        response = self.client.post(
            f'/api/tasks/{task.id}/copy/',
            {'include_children': False},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 2)
        copied_task = Task.objects.exclude(id=task.id).first()
        self.assertEqual(copied_task.title, 'Kopia: Original Task')
        self.assertEqual(copied_task.progress, 50)

    def test_copy_task_with_custom_title(self):
        """Test copying a task with custom title."""
        task = Task.objects.create(
            project=self.project,
            title='Original Task',
            status='todo',
            assignee=self.user
        )
        response = self.client.post(
            f'/api/tasks/{task.id}/copy/',
            {'title': 'Custom Copy Title'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        copied_task = Task.objects.exclude(id=task.id).first()
        self.assertEqual(copied_task.title, 'Custom Copy Title')

    def test_unauthenticated_access(self):
        """Test that unauthenticated users cannot access tasks."""
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/tasks/')
        # IsAuthenticatedOrReadOnly returns 403 for unauthenticated users on non-GET
        # But for GET it might return 403 or 401 depending on permission class
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_duration_days_field(self):
        """Test that duration_days is calculated correctly."""
        task = Task.objects.create(
            project=self.project,
            title='Test Task',
            status='todo',
            assignee=self.user,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=10)
        )
        response = self.client.get(f'/api/tasks/{task.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['duration_days'], 10)


class DependencyAPITestCase(TestCase):
    """Test cases for Dependency API endpoints."""

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
            name='Test Project',
            description='Test description',
            status='active',
            priority=2,
            owner=self.user
        )
        self.other_project = Project.objects.create(
            name='Other Project',
            description='Other description',
            status='active',
            priority=2,
            owner=self.other_user
        )
        self.task1 = Task.objects.create(
            project=self.project,
            title='Task 1',
            status='todo',
            assignee=self.user
        )
        self.task2 = Task.objects.create(
            project=self.project,
            title='Task 2',
            status='todo',
            assignee=self.user
        )
        self.client.force_authenticate(user=self.user)

    def test_list_dependencies(self):
        """Test listing all dependencies."""
        dep = Dependency.objects.create(
            predecessor=self.task1,
            successor=self.task2,
            type='FS'
        )
        response = self.client.get('/api/dependencies/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_create_dependency(self):
        """Test creating a new dependency."""
        data = {
            'predecessor': self.task1.id,
            'successor': self.task2.id,
            'type': 'FS',
            'lag_days': 0
        }
        response = self.client.post('/api/dependencies/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Dependency.objects.count(), 1)
        dep = Dependency.objects.get()
        self.assertEqual(dep.predecessor, self.task1)
        self.assertEqual(dep.successor, self.task2)
        self.assertEqual(dep.type, 'FS')

    def test_create_dependency_required_fields(self):
        """Test that required fields are validated."""
        data = {
            'type': 'FS'
        }
        response = self.client.post('/api/dependencies/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_dependency_different_projects(self):
        """Test that dependencies between tasks from different projects are rejected."""
        other_task = Task.objects.create(
            project=self.other_project,
            title='Other Task',
            status='todo',
            assignee=self.other_user
        )
        data = {
            'predecessor': self.task1.id,
            'successor': other_task.id,
            'type': 'FS'
        }
        response = self.client.post('/api/dependencies/', data, format='json')
        # ValidationError from model is raised, which DRF converts to 400
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Check that error message mentions projects
        self.assertIn('projekt', str(response.data).lower())

    def test_create_dependency_self_reference(self):
        """Test that self-referencing dependencies are rejected."""
        data = {
            'predecessor': self.task1.id,
            'successor': self.task1.id,
            'type': 'FS'
        }
        response = self.client.post('/api/dependencies/', data, format='json')
        # ValidationError from model is raised, which DRF converts to 400
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Check that error message mentions self-reference
        self.assertIn('samego siebie', str(response.data).lower())

    def test_create_dependency_cycle(self):
        """Test that circular dependencies are rejected."""
        task3 = Task.objects.create(
            project=self.project,
            title='Task 3',
            status='todo',
            assignee=self.user
        )
        # Create first dependency
        Dependency.objects.create(
            predecessor=self.task1,
            successor=self.task2,
            type='FS'
        )
        Dependency.objects.create(
            predecessor=self.task2,
            successor=task3,
            type='FS'
        )
        # Try to create cycle
        data = {
            'predecessor': task3.id,
            'successor': self.task1.id,
            'type': 'FS'
        }
        response = self.client.post('/api/dependencies/', data, format='json')
        # ValidationError from model is raised, which DRF converts to 400
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Check that error message mentions cycle
        self.assertIn('cykl', str(response.data).lower())

    def test_retrieve_dependency(self):
        """Test retrieving a single dependency."""
        dep = Dependency.objects.create(
            predecessor=self.task1,
            successor=self.task2,
            type='FS'
        )
        response = self.client.get(f'/api/dependencies/{dep.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['predecessor'], self.task1.id)
        self.assertEqual(response.data['successor'], self.task2.id)
        self.assertEqual(response.data['type'], 'FS')

    def test_update_dependency_as_project_owner(self):
        """Test updating a dependency as project owner."""
        dep = Dependency.objects.create(
            predecessor=self.task1,
            successor=self.task2,
            type='FS',
            lag_days=0
        )
        data = {
            'predecessor': self.task1.id,
            'successor': self.task2.id,
            'type': 'SS',
            'lag_days': 5
        }
        response = self.client.put(f'/api/dependencies/{dep.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        dep.refresh_from_db()
        self.assertEqual(dep.type, 'SS')
        self.assertEqual(dep.lag_days, 5)

    def test_update_dependency_as_non_owner(self):
        """Test that non-owners cannot update dependencies."""
        dep = Dependency.objects.create(
            predecessor=self.task1,
            successor=self.task2,
            type='FS'
        )
        self.client.force_authenticate(user=self.other_user)
        data = {
            'predecessor': self.task1.id,
            'successor': self.task2.id,
            'type': 'SS',
            'lag_days': 5
        }
        response = self.client.put(f'/api/dependencies/{dep.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_dependency(self):
        """Test deleting a dependency."""
        dep = Dependency.objects.create(
            predecessor=self.task1,
            successor=self.task2,
            type='FS'
        )
        response = self.client.delete(f'/api/dependencies/{dep.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Dependency.objects.count(), 0)

    def test_unauthenticated_access(self):
        """Test that unauthenticated users cannot access dependencies."""
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/dependencies/')
        # IsAuthenticatedOrReadOnly returns 403 for unauthenticated users
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])
