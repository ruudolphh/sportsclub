# scheduling/models/competition.py
from django.core.exceptions import ValidationError
from django.db import models
from pydantic import ValidationError as PydanticValidationError

from scheduling.models.activity import Activity
from scheduling.schemas import CompetitionScore


class Competition(Activity):
    """A competitive with multiple individuals, usually with a result."""

    score = models.JSONField(blank=True, null=True, help_text="Aggregate score summary")

    def clean(self):
        super().clean()
        if self.score is not None:
            try:
                CompetitionScore.model_validate(self.score)
            except PydanticValidationError as err:
                raise ValidationError({"score": str(err)}) from err

    class Meta:
        verbose_name = "Competition"
        verbose_name_plural = "Competitions"
        ordering = ["-date"]
