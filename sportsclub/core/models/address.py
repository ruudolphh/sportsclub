# core/models/address.py
from django.db import models
from django.db.models import Count, QuerySet
from nanoid_field import NanoidField

from core.models.auditory import Auditory


class Address(Auditory):
    """A postal address."""

    id = models.BigAutoField(primary_key=True)
    public_id = NanoidField(unique=True, editable=False, db_index=True)
    line1 = models.CharField(max_length=255)
    line2 = models.CharField(max_length=255, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)

    class Meta:
        verbose_name = "Address"
        verbose_name_plural = "Addresses"
        # Composite index that can be used for queries that filter on:
        # The first field only.
        # The first and second fields.
        # E.g., "Venues in Palma, Spain".
        indexes = [
            models.Index(fields=["city", "country"]),
        ]

    def __str__(self) -> str:
        """
        Format address in Google Maps style.
        Example: "Av. de Jaume III, 15, Centre, 07012 Palma, Illes Balears, Spain"
        """
        parts = []

        # Address lines
        parts.append(self.line1)
        if self.line2:
            parts.append(self.line2)

        # Postal code and city
        city_part = []
        if self.postal_code:
            city_part.append(self.postal_code)
        if self.city:
            city_part.append(self.city)
        if city_part:
            parts.append(" ".join(city_part))

        # State
        if self.state:
            parts.append(self.state)

        # Country
        if self.country:
            parts.append(self.country)

        return ", ".join(parts)

    @classmethod
    def get_orphaned_addresses(cls) -> QuerySet["Address"]:
        """
        Find addresses that are not referenced by any entity, used by cleanup tasks.

        Returns:
            QuerySet of `Address` objects with no foreign key references
        """
        orphaned = cls.objects.annotate(
            athlete_count=Count("athlete", distinct=True),
            venue_count=Count("venue", distinct=True),
            coach_count=Count("coach", distinct=True),
        ).filter(
            athlete_count=0,
            venue_count=0,
            coach_count=0,
        )
        return orphaned
