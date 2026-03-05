# scheduling/models/activity.py
from core.models import Auditory
from django.db import models
from inventory.models import Venue
from nanoid_field import NanoidField
from people.models import Athlete, Coach

from scheduling.models.season import Season


class Activity(Auditory):
    """Base model for activities (competitions, trainings, etc.)."""

    id = models.BigAutoField(primary_key=True)
    public_id = NanoidField(unique=True, editable=False)
    name = models.CharField(max_length=255)
    date = models.DateTimeField()

    venue = models.ForeignKey(
        Venue,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_activities",
    )
    season = models.ForeignKey(
        Season,
        on_delete=models.CASCADE,
        related_name="%(class)s_activities",
    )
    coaches = models.ManyToManyField(
        Coach,
        blank=True,
        related_name="%(class)s_activities",
    )
    athletes = models.ManyToManyField(
        Athlete,
        blank=True,
        related_name="%(class)s_activities",
    )

    class Meta:
        abstract = True
        ordering = ["-date"]

    def __str__(self):
        return f"{self.name} ({self.date.strftime('%Y-%m-%d')})"
