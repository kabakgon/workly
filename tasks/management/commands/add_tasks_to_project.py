from django.core.management.base import BaseCommand
from tasks.models import Task
from projects.models import Project
from django.contrib.auth import get_user_model
from datetime import date, timedelta

User = get_user_model()


class Command(BaseCommand):
    help = 'Adds tasks to project with id=5 for Gantt chart visualization'

    def handle(self, *args, **options):
        # Get project with id=5
        try:
            project = Project.objects.get(id=5)
            self.stdout.write(self.style.SUCCESS(f'Znaleziono projekt: {project.name}'))
        except Project.DoesNotExist:
            self.stdout.write(self.style.ERROR('Błąd: Projekt o id=5 nie istnieje!'))
            return

        # Get first user (or admin) for assignee
        user = User.objects.first()
        if not user:
            self.stdout.write(self.style.ERROR('Błąd: Brak użytkowników w bazie!'))
            return

        # Base date - start from today
        base_date = date.today()

        # Task templates with dates
        tasks_data = [
            {
                "title": "Analiza wymagań",
                "description": "Przeprowadzenie szczegółowej analizy wymagań projektu",
                "status": "in_progress",
                "start_date": base_date,
                "end_date": base_date + timedelta(days=5),
                "progress": 30,
            },
            {
                "title": "Projektowanie architektury",
                "description": "Zaprojektowanie architektury systemu",
                "status": "todo",
                "start_date": base_date + timedelta(days=3),
                "end_date": base_date + timedelta(days=10),
                "progress": 0,
            },
            {
                "title": "Implementacja backendu",
                "description": "Implementacja logiki biznesowej i API",
                "status": "todo",
                "start_date": base_date + timedelta(days=8),
                "end_date": base_date + timedelta(days=20),
                "progress": 0,
            },
            {
                "title": "Implementacja frontendu",
                "description": "Tworzenie interfejsu użytkownika",
                "status": "todo",
                "start_date": base_date + timedelta(days=15),
                "end_date": base_date + timedelta(days=28),
                "progress": 0,
            },
            {
                "title": "Testy jednostkowe",
                "description": "Pisanie i wykonywanie testów jednostkowych",
                "status": "todo",
                "start_date": base_date + timedelta(days=18),
                "end_date": base_date + timedelta(days=25),
                "progress": 0,
            },
            {
                "title": "Testy integracyjne",
                "description": "Testowanie integracji między komponentami",
                "status": "todo",
                "start_date": base_date + timedelta(days=22),
                "end_date": base_date + timedelta(days=30),
                "progress": 0,
            },
            {
                "title": "Dokumentacja techniczna",
                "description": "Przygotowanie dokumentacji technicznej",
                "status": "todo",
                "start_date": base_date + timedelta(days=25),
                "end_date": base_date + timedelta(days=32),
                "progress": 0,
            },
            {
                "title": "Przegląd kodu",
                "description": "Code review i refaktoryzacja",
                "status": "todo",
                "start_date": base_date + timedelta(days=28),
                "end_date": base_date + timedelta(days=35),
                "progress": 0,
            },
            {
                "title": "Wdrożenie na środowisko testowe",
                "description": "Deployment na środowisko testowe",
                "status": "todo",
                "start_date": base_date + timedelta(days=32),
                "end_date": base_date + timedelta(days=35),
                "progress": 0,
            },
            {
                "title": "Testy akceptacyjne",
                "description": "Przeprowadzenie testów akceptacyjnych",
                "status": "todo",
                "start_date": base_date + timedelta(days=33),
                "end_date": base_date + timedelta(days=38),
                "progress": 0,
            },
            {
                "title": "Wdrożenie produkcyjne",
                "description": "Deployment na środowisko produkcyjne",
                "status": "todo",
                "start_date": base_date + timedelta(days=38),
                "end_date": base_date + timedelta(days=40),
                "progress": 0,
            },
            {
                "title": "Szkolenie użytkowników",
                "description": "Przeprowadzenie szkoleń dla użytkowników końcowych",
                "status": "todo",
                "start_date": base_date + timedelta(days=40),
                "end_date": base_date + timedelta(days=45),
                "progress": 0,
            },
        ]

        # Create tasks
        created_tasks = []
        for task_data in tasks_data:
            task = Task.objects.create(
                project=project,
                assignee=user,
                **task_data
            )
            created_tasks.append(task)
            self.stdout.write(f'Utworzono zadanie: {task.title} (ID: {task.id})')

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Utworzono {len(created_tasks)} zadań dla projektu "{project.name}" (ID: {project.id})'
            )
        )
        self.stdout.write(
            f'Zadania mają daty od {base_date} do {base_date + timedelta(days=45)}'
        )

