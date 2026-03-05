# scheduling/models/training.py
from django.db import models

from scheduling.models.activity import Activity


class Training(Activity):
    """A practice session aimed at skill development."""

    focus = models.CharField(
        max_length=255, blank=True, help_text="Main focus of the training session"
    )

    class Meta:
        verbose_name = "Training session"
        verbose_name_plural = "Training sessions"
        ordering = ["-date"]
