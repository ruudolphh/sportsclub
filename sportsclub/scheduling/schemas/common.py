# scheduling/schemas/common.py
from core.models.enums import Discipline
from ninja import Schema
from pydantic import Field


class MedalCount(Schema):
    """Medal count for a discipline."""

    gold: int = Field(default=0, ge=0, description="1st place")
    silver: int = Field(default=0, ge=0, description="2nd place")
    bronze: int = Field(default=0, ge=0, description="3rd place")


class CompetitionScore(Schema):
    """Aggregate score summary for a competition.

    Validates JSON documents like:

    "results": {
        "sprints": {"gold": 2, "silver": 1, "bronze": 3},
        "high_jump": {"gold": 1, "silver": 0, "bronze": 1}
    }
    """

    results: dict[Discipline, MedalCount] = Field(default_factory=dict)

    model_config = {"extra": "forbid"}
