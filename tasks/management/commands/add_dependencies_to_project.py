from django.core.management.base import BaseCommand
from tasks.models import Task, Dependency
from projects.models import Project
from django.db import transaction
from django.core.exceptions import ValidationError


class Command(BaseCommand):
    help = 'Adds dependencies to tasks in project with id=5 for Gantt chart visualization'

    def handle(self, *args, **options):
        # Get project with id=5
        try:
            project = Project.objects.get(id=5)
            self.stdout.write(self.style.SUCCESS(f'Znaleziono projekt: {project.name}'))
        except Project.DoesNotExist:
            self.stdout.write(self.style.ERROR('Błąd: Projekt o id=5 nie istnieje!'))
            return

        # Get all tasks from project
        tasks = Task.objects.filter(project=project).order_by('id')
        task_list = list(tasks)
        
        if len(task_list) < 2:
            self.stdout.write(self.style.ERROR('Błąd: Projekt musi mieć co najmniej 2 zadania!'))
            return

        self.stdout.write(f'Znaleziono {len(task_list)} zadań w projekcie')
        
        # Create dependencies - sequential flow
        dependencies_created = []
        
        with transaction.atomic():
            # Create a chain of dependencies: task1 -> task2 -> task3 -> etc.
            # This creates a simple sequential flow without cycles
            for i in range(len(task_list) - 1):
                predecessor = task_list[i]
                successor = task_list[i + 1]
                
                # Check if dependency already exists (any type)
                existing = Dependency.objects.filter(
                    predecessor=predecessor,
                    successor=successor
                ).first()
                
                if not existing:
                    try:
                        dep = Dependency(
                            predecessor=predecessor,
                            successor=successor,
                            type='FS',  # Finish-to-Start
                            lag_days=0
                        )
                        dep.full_clean()  # Validate before saving
                        dep.save()
                        dependencies_created.append(dep)
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'✓ Utworzono zależność: "{predecessor.title}" -> "{successor.title}" (FS)'
                            )
                        )
                    except ValidationError as e:
                        error_msg = str(e) if hasattr(e, '__str__') else (e.message_dict if hasattr(e, 'message_dict') else 'Nieznany błąd walidacji')
                        self.stdout.write(
                            self.style.WARNING(
                                f'⚠ Nie można utworzyć zależności "{predecessor.title}" -> "{successor.title}": {error_msg}'
                            )
                        )
                else:
                    self.stdout.write(
                        f'  Zależność już istnieje: "{predecessor.title}" -> "{successor.title}"'
                    )
            
            # Add some parallel dependencies for better visualization
            # Only add if they don't create cycles
            if len(task_list) >= 5:
                # Task 1 -> Task 3 (skip task 2)
                task1 = task_list[0]
                task3 = task_list[2]
                
                existing = Dependency.objects.filter(
                    predecessor=task1,
                    successor=task3
                ).first()
                
                if not existing:
                    try:
                        dep = Dependency(
                            predecessor=task1,
                            successor=task3,
                            type='FS',
                            lag_days=0
                        )
                        dep.full_clean()
                        dep.save()
                        dependencies_created.append(dep)
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'✓ Utworzono równoległą zależność: "{task1.title}" -> "{task3.title}" (FS)'
                            )
                        )
                    except ValidationError as e:
                        error_msg = str(e) if hasattr(e, '__str__') else (e.message_dict if hasattr(e, 'message_dict') else 'Nieznany błąd walidacji')
                        self.stdout.write(
                            self.style.WARNING(
                                f'⚠ Nie można utworzyć równoległej zależności "{task1.title}" -> "{task3.title}": {error_msg}'
                            )
                        )
            
            # Add another parallel dependency if possible
            if len(task_list) >= 6:
                # Task 2 -> Task 5 (skip tasks 3 and 4)
                task2 = task_list[1]
                task5 = task_list[4]
                
                existing = Dependency.objects.filter(
                    predecessor=task2,
                    successor=task5
                ).first()
                
                if not existing:
                    try:
                        dep = Dependency(
                            predecessor=task2,
                            successor=task5,
                            type='FS',
                            lag_days=0
                        )
                        dep.full_clean()
                        dep.save()
                        dependencies_created.append(dep)
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'✓ Utworzono równoległą zależność: "{task2.title}" -> "{task5.title}" (FS)'
                            )
                        )
                    except ValidationError as e:
                        error_msg = str(e) if hasattr(e, '__str__') else (e.message_dict if hasattr(e, 'message_dict') else 'Nieznany błąd walidacji')
                        self.stdout.write(
                            self.style.WARNING(
                                f'⚠ Nie można utworzyć równoległej zależności "{task2.title}" -> "{task5.title}": {error_msg}'
                            )
                        )

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Utworzono {len(dependencies_created)} nowych zależności dla projektu "{project.name}" (ID: {project.id})'
            )
        )

