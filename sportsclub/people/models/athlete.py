# people/models/athlete.py
from django.db import models

from .person import Person


class Athlete(Person):
    """People practising sports."""

    height = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    jersey_number = models.IntegerField(null=True, blank=True)
