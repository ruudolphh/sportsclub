# inventory/models/venue.py
from core.models import Address, Auditory
from django.db import models
from nanoid_field import NanoidField


class VenueType(models.TextChoices):
    """Venue types."""

    STADIUM = "stadium", "Stadium"
    GYMNASIUM = "gymnasium", "Gymnasium"
    TRACK = "TRACK", "Track"
    FIELD = "FIELD", "Field"


class Venue(Auditory):
    """Locations where sports are practised."""

    id = models.BigAutoField(primary_key=True)
    public_id = NanoidField(unique=True, editable=False)

    name = models.CharField(max_length=200)
    venue_type = models.CharField(
        max_length=20, choices=VenueType.choices, default=VenueType.FIELD
    )
    capacity = models.PositiveIntegerField(null=True, blank=True)
    address = models.ForeignKey(
        Address, null=True, blank=True, on_delete=models.SET_NULL
    )
    indoor = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Venue"
        verbose_name_plural = "Venues"

    def __str__(self) -> str:
        return self.name
