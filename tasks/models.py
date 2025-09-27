from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model
from projects.models import Project
from django.core.exceptions import ValidationError
from django.db.models import Q, F

User = get_user_model()


class Task(models.Model):
    class Status(models.TextChoices):
        TODO = "todo", "Do zrobienia"
        IN_PROGRESS = "in_progress", "W toku"
        REVIEW = "review", "Weryfikacja"
        DONE = "done", "Zrobione"
        BLOCKED = "blocked", "Zablokowane"

    project = models.ForeignKey(
        Project, on_delete=models.PROTECT, related_name="tasks", verbose_name="Projekt"
    )
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
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
        default=0, verbose_name="Indeks sortowania", editable=False
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

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data utworzenia")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Data aktualizacji")

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


# --- Model zależności między zadaniami ---
class Dependency(models.Model):
    class Type(models.TextChoices):
        FS = "FS", "Koniec→Start"
        SS = "SS", "Start→Start"
        FF = "FF", "Koniec→Koniec"
        SF = "SF", "Start→Koniec"

    predecessor = models.ForeignKey(
        Task,
        on_delete=models.PROTECT,
        related_name="as_predecessor",
        verbose_name="Poprzednik",
    )
    successor = models.ForeignKey(
        Task,
        on_delete=models.PROTECT,
        related_name="as_successor",
        verbose_name="Następnik",
    )
    type = models.CharField(
        max_length=2,
        choices=Type.choices,
        default=Type.FS,
        verbose_name="Typ zależności",
    )
    lag_days = models.IntegerField(default=0, verbose_name="Liczba dni opóźnienia")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data utworzenia")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Data aktualizacji")

    class Meta:
        verbose_name = "Zależność"
        verbose_name_plural = "Zależności"
        constraints = [
            # zakaz duplikatów: ten sam łuk + typ tylko raz
            models.UniqueConstraint(
                fields=["predecessor", "successor", "type"],
                name="uniq_dependency_edge_type",
            ),
            # zakaz zależności zadania od samego siebie
            models.CheckConstraint(
                check=~Q(predecessor=F("successor")),
                name="no_self_dependency",
            ),
        ]

    def __str__(self):
        return (
            f"{self.predecessor_id} {self.type}→ {self.successor_id} ({self.lag_days}d)"
        )

    def clean(self):
        # ten check jest na poziomie aplikacji (DB nie zrobi joinów po projekcie)
        if self.predecessor_id and self.successor_id:
            if self.predecessor_id == self.successor_id:
                raise ValidationError("Zadanie nie może zależeć od samego siebie.")
            if self.predecessor.project_id != self.successor.project_id:
                raise ValidationError(
                    "Oba zadania w zależności muszą należeć do tego samego projektu."
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
