# scheduling/schemas/training.py
from datetime import datetime

from inventory.schemas import VenueRef
from ninja import Field, Schema
from people.schemas import AthleteRef, CoachRef

from scheduling.schemas.season import SeasonRef


class TrainingIn(Schema):
    """Schema for creating and fully updating a training session (POST, PUT)."""

    name: str = Field(..., min_length=1, max_length=255)
    date: datetime
    venue_public_id: str | None = None
    season_public_id: str = Field(..., description="Season the training belongs to")
    coach_public_ids: list[str] = Field(default_factory=list)
    athlete_public_ids: list[str] = Field(default_factory=list)
    focus: str = Field("", max_length=255)


class TrainingPatch(Schema):
    """Schema for partially updating a training session (PATCH). All fields optional."""

    name: str | None = Field(None, min_length=1, max_length=255)
    date: datetime | None = None
    venue_public_id: str | None = None
    season_public_id: str | None = None
    coach_public_ids: list[str] | None = None
    athlete_public_ids: list[str] | None = None
    focus: str | None = Field(None, max_length=255)


class TrainingListOut(Schema):
    """Schema for listing training sessions (minimal fields)."""

    public_id: str
    name: str
    date: datetime
    season: SeasonRef
    focus: str

    @staticmethod
    def resolve_season(obj):
        return obj.season


class TrainingOut(Schema):
    """Schema for full training session details."""

    public_id: str
    name: str
    date: datetime
    venue: VenueRef | None
    season: SeasonRef
    coaches: list[CoachRef]
    athletes: list[AthleteRef]
    focus: str

    @staticmethod
    def resolve_venue(obj):
        return obj.venue if obj.venue else None

    @staticmethod
    def resolve_season(obj):
        return obj.season

    @staticmethod
    def resolve_coaches(obj):
        return list(obj.coaches.all())

    @staticmethod
    def resolve_athletes(obj):
        return list(obj.athletes.all())
