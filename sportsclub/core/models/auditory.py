# core/models/auditory.py
from django.db import models
from django.utils import timezone

from .managers import SoftDeleteManager


class Auditory(models.Model):
    """
    Base class for auditory fields with support for soft-deletion.
    It does not implement anonymisation or purging of records.
    It does not keep track of which user last performed a given operation.
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    # Default manager that excludes soft-deleted records
    objects = SoftDeleteManager()

    # Manager to access all records including soft-deleted
    all_objects = models.Manager()

    class Meta:
        abstract = True

    def soft_delete(self):
        """Mark record as deleted without removing from database."""

        self.deleted_at = timezone.now()
        self.save(update_fields=["deleted_at", "updated_at"])

    def restore(self):
        """Restore a soft-deleted record."""

        self.deleted_at = None
        self.save(update_fields=["deleted_at", "updated_at"])

    # Query Helpers
    @classmethod
    def get_soft_deleted(cls):
        """Get only soft-deleted records."""
        return cls.all_objects.filter(deleted_at__isnull=False)

    # Properties
    @property
    def is_soft_deleted(self):
        """Check if record is soft deleted."""
        return self.deleted_at is not None
