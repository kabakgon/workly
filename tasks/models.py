from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model
from projects.models import Project

User = get_user_model()


class Task(models.Model):
    class Status(models.TextChoices):
        TODO = "todo", "Do zrobienia"
        IN_PROGRESS = "in_progress", "W toku"
        REVIEW = "review", "Przegląd"
        DONE = "done", "Zrobione"
        BLOCKED = "blocked", "Zablokowane"

    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="tasks", verbose_name="Projekt"
    )
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="children",
        verbose_name="Zadanie nadrzędne",
    )

    title = models.CharField(max_length=160, verbose_name="Tytuł")
    description = models.TextField(blank=True, verbose_name="Opis")
    assignee = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="tasks",
        verbose_name="Przypisany użytkownik",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.TODO,
        verbose_name="Status",
    )
    start_date = models.DateField(
        null=True, blank=True, verbose_name="Data rozpoczęcia"
    )
    end_date = models.DateField(null=True, blank=True, verbose_name="Data zakończenia")

    progress = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Postęp (%)",
    )
    sort_index = models.PositiveIntegerField(
        default=0, verbose_name="Indeks sortowania"
    )

    estimated_hours = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Szacowane godziny",
    )
    actual_hours = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Rzeczywiste godziny",
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Utworzono")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Zaktualizowano")

    class Meta:
        verbose_name = "Zadanie"
        verbose_name_plural = "Zadania"
        ordering = ["project", "sort_index", "id"]

    def __str__(self):
        return self.title

    @property
    def duration_days(self):
        if self.start_date and self.end_date:
            return max((self.end_date - self.start_date).days, 0)
        return None
