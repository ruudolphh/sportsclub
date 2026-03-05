# scheduling/models/season.py
from core.models import Auditory
from django.db import models
from nanoid_field import NanoidField


class Season(Auditory):
    """A time range groupping activities."""

    id = models.BigAutoField(primary_key=True)
    public_id = NanoidField(unique=True, editable=False)
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()

    class Meta:
        verbose_name = "Season"
        verbose_name_plural = "Seasons"
        ordering = ["-start_date"]

    def __str__(self):
        return self.name
