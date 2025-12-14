"""
Django management command to set up demo data for Workly 2.0.

This command:
- Adds 3 new demo users
- Deletes all existing projects and tasks
- Creates new demo projects with realistic names
- Adds 10 tasks to each project with various statuses, dates, and assignments

Usage:
    python manage.py setup_demo_data
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date, timedelta
import random

from projects.models import Project
from tasks.models import Task, Dependency

User = get_user_model()


class Command(BaseCommand):
    help = 'Set up demo data for Workly 2.0'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Rozpoczynam konfigurację bazy demo...'))
        
        # Step 1: Add demo users
        self.stdout.write('\n📝 Dodawanie użytkowników demo...')
        demo_users = self.create_demo_users()
        
        # Step 2: Delete all existing projects and tasks
        self.stdout.write('\n🗑️  Usuwanie istniejących projektów i zadań...')
        self.delete_all_data()
        
        # Step 3: Create demo projects
        self.stdout.write('\n📁 Tworzenie projektów demo...')
        projects = self.create_demo_projects(demo_users)
        
        # Step 4: Add tasks to each project
        self.stdout.write('\n✅ Dodawanie zadań do projektów...')
        for project in projects:
            self.add_tasks_to_project(project, demo_users)
        
        self.stdout.write(self.style.SUCCESS('\n✨ Baza demo została pomyślnie skonfigurowana!'))
        self.stdout.write(f'   - Utworzono {len(demo_users)} użytkowników')
        self.stdout.write(f'   - Utworzono {len(projects)} projektów')
        self.stdout.write(f'   - Utworzono {len(projects) * 10} zadań')
        
        # Display login info
        self.stdout.write('\n📋 Informacje logowania dla użytkowników demo:')
        for user in demo_users:
            self.stdout.write(f'   - {user.username} / hasło: 1 / email: {user.email}')

    def create_demo_users(self):
        """Create 3 demo users with password '1'"""
        demo_users_data = [
            {'username': 'anna_kowalska', 'email': 'anna.kowalska@workly.demo', 'first_name': 'Anna', 'last_name': 'Kowalska'},
            {'username': 'piotr_nowak', 'email': 'piotr.nowak@workly.demo', 'first_name': 'Piotr', 'last_name': 'Nowak'},
            {'username': 'maria_wisniewska', 'email': 'maria.wisniewska@workly.demo', 'first_name': 'Maria', 'last_name': 'Wiśniewska'},
        ]
        
        demo_users = []
        for user_data in demo_users_data:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                }
            )
            if created:
                user.set_password('1')
                user.save()
                self.stdout.write(f'   ✓ Utworzono użytkownika: {user.username}')
            else:
                # Update password if user exists
                user.set_password('1')
                user.save()
                self.stdout.write(f'   ↻ Zaktualizowano hasło dla: {user.username}')
            demo_users.append(user)
        
        return demo_users

    def delete_all_data(self):
        """Delete all projects and tasks (must delete dependencies first due to PROTECT)"""
        dependency_count = Dependency.objects.count()
        task_count = Task.objects.count()
        project_count = Project.objects.count()
        
        # Delete in correct order due to PROTECT constraints:
        # 1. Delete dependencies first (they reference tasks with PROTECT)
        Dependency.objects.all().delete()
        
        # 2. Clear parent relationships (Task.parent uses PROTECT)
        Task.objects.update(parent=None)
        
        # 3. Now we can delete tasks
        Task.objects.all().delete()
        
        # 4. Finally delete projects
        Project.objects.all().delete()
        
        self.stdout.write(f'   ✓ Usunięto {dependency_count} zależności')
        self.stdout.write(f'   ✓ Usunięto {task_count} zadań')
        self.stdout.write(f'   ✓ Usunięto {project_count} projektów')

    def create_demo_projects(self, users):
        """Create demo projects with realistic names"""
        projects_data = [
            {
                'name': 'System Zarządzania Projektami',
                'description': 'Rozwój kompleksowego systemu do zarządzania projektami z funkcjami śledzenia zadań, raportowania i współpracy zespołowej.',
                'status': 'active',
                'priority': 3,
            },
            {
                'name': 'Aplikacja Mobilna E-Commerce',
                'description': 'Tworzenie natywnej aplikacji mobilnej dla sklepu internetowego z integracją płatności i powiadomień push.',
                'status': 'active',
                'priority': 4,
            },
            {
                'name': 'Portal Klienta B2B',
                'description': 'Budowa portalu dla klientów biznesowych z możliwością składania zamówień, śledzenia statusu i zarządzania kontami.',
                'status': 'active',
                'priority': 3,
            },
            {
                'name': 'System Analizy Danych',
                'description': 'Implementacja systemu do analizy i wizualizacji danych biznesowych z dashboardami i raportami automatycznymi.',
                'status': 'planned',
                'priority': 2,
            },
            {
                'name': 'Migracja do Chmury',
                'description': 'Przeniesienie infrastruktury IT do środowiska chmurowego z optymalizacją kosztów i zwiększeniem wydajności.',
                'status': 'active',
                'priority': 4,
            },
        ]
        
        projects = []
        base_date = date.today()
        
        for i, project_data in enumerate(projects_data):
            # Assign random owner from demo users
            owner = random.choice(users)
            
            # Set dates - some projects started earlier
            start_date = base_date - timedelta(days=random.randint(0, 30))
            end_date = start_date + timedelta(days=random.randint(60, 120))
            
            project = Project.objects.create(
                name=project_data['name'],
                description=project_data['description'],
                start_date=start_date,
                end_date=end_date,
                status=project_data['status'],
                priority=project_data['priority'],
                owner=owner,
            )
            projects.append(project)
            self.stdout.write(f'   ✓ Utworzono projekt: {project.name} (właściciel: {owner.username})')
        
        return projects

    def add_tasks_to_project(self, project, users):
        """Add 10 tasks to a project with various statuses, dates, and assignments"""
        base_date = project.start_date
        statuses = ['todo', 'in_progress', 'review', 'done', 'blocked']
        status_weights = [0.2, 0.3, 0.2, 0.25, 0.05]  # More in_progress and done, fewer blocked
        
        task_templates = [
            {'title': 'Analiza wymagań', 'description': 'Przeprowadzenie szczegółowej analizy wymagań biznesowych i technicznych'},
            {'title': 'Projektowanie architektury', 'description': 'Zaprojektowanie architektury systemu i wybór technologii'},
            {'title': 'Przygotowanie środowiska deweloperskiego', 'description': 'Konfiguracja środowiska deweloperskiego i narzędzi'},
            {'title': 'Implementacja backendu', 'description': 'Rozwój logiki biznesowej i API backendowego'},
            {'title': 'Implementacja frontendu', 'description': 'Tworzenie interfejsu użytkownika i integracja z backendem'},
            {'title': 'Testy jednostkowe', 'description': 'Pisanie i wykonywanie testów jednostkowych dla kluczowych komponentów'},
            {'title': 'Testy integracyjne', 'description': 'Testowanie integracji między komponentami systemu'},
            {'title': 'Dokumentacja techniczna', 'description': 'Przygotowanie dokumentacji technicznej i API'},
            {'title': 'Code review i refaktoryzacja', 'description': 'Przegląd kodu i optymalizacja wydajności'},
            {'title': 'Wdrożenie na środowisko testowe', 'description': 'Deployment na środowisko testowe i weryfikacja'},
        ]
        
        created_tasks = []
        current_date = base_date
        
        for i, template in enumerate(task_templates):
            # Random status based on weights
            status = random.choices(statuses, weights=status_weights)[0]
            
            # Random assignee (can be None)
            assignee = random.choice([None] + users) if random.random() > 0.1 else None
            
            # Calculate dates - tasks should be within project dates
            days_offset = random.randint(0, (project.end_date - project.start_date).days - 14)
            task_start = project.start_date + timedelta(days=days_offset)
            task_duration = random.randint(3, 14)
            task_end = min(task_start + timedelta(days=task_duration), project.end_date)
            
            # Progress based on status
            if status == 'done':
                progress = random.randint(90, 100)
            elif status == 'review':
                progress = random.randint(70, 90)
            elif status == 'in_progress':
                progress = random.randint(20, 70)
            elif status == 'blocked':
                progress = random.randint(0, 30)
            else:  # todo
                progress = random.randint(0, 20)
            
            task = Task.objects.create(
                project=project,
                title=template['title'],
                description=template['description'],
                start_date=task_start,
                end_date=task_end,
                status=status,
                progress=progress,
                assignee=assignee,
            )
            created_tasks.append(task)
        
        self.stdout.write(f'   ✓ Dodano 10 zadań do projektu: {project.name}')
        
        return created_tasks

