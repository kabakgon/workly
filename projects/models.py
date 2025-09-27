from django.db import models

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Project(models.Model):
    class Status(models.TextChoices):
        PLANNED = "planned", "Planowany"
        ACTIVE = "active", "Aktywny"
        ON_HOLD = "on_hold", "Wstrzymany"
        DONE = "done", "Zakończony"
        ARCHIVED = "archived", "Zarchiwizowany"

    class Priority(models.IntegerChoices):
        LOW = 1, "Niski"
        MEDIUM = 2, "Średni"
        HIGH = 3, "Wysoki"
        CRITICAL = 4, "Krytyczny"

    name = models.CharField(max_length=120, unique=True, verbose_name="Nazwa")
    description = models.TextField(blank=True, verbose_name="Opis")
    start_date = models.DateField(
        null=True, blank=True, verbose_name="Data rozpoczęcia"
    )
    end_date = models.DateField(null=True, blank=True, verbose_name="Data zakończenia")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PLANNED,
        blank=False,
        null=False,
        verbose_name="Status",
    )
    priority = models.IntegerField(
        choices=Priority.choices,
        default=Priority.MEDIUM,
        blank=False,
        null=False,
        verbose_name="Priorytet",
    )
    owner = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="owned_projects",
        verbose_name="Właściciel",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data utworzenia")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Data aktualizacji")

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name
