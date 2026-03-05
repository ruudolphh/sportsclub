# scheduling/schemas/activity.py
from datetime import datetime

from inventory.schemas import VenueRef
from ninja import Field, Schema
from people.schemas import AthleteRef, CoachRef

from scheduling.schemas.season import SeasonRef


class ActivityIn(Schema):
    """Schema for creating and fully updating an activity (POST, PUT)."""

    name: str = Field(..., min_length=1, max_length=255)
    date: datetime
    venue_public_id: str | None = None
    season_public_id: str
    coach_public_ids: list[str] = Field(default_factory=list)
    athlete_public_ids: list[str] = Field(default_factory=list)


class ActivityPatch(Schema):
    """Schema for partially updating an activity (PATCH). All fields optional."""

    name: str | None = Field(None, min_length=1, max_length=255)
    date: datetime | None = None
    venue_public_id: str | None = None
    season_public_id: str | None = None
    coach_public_ids: list[str] | None = None
    athlete_public_ids: list[str] | None = None


class ActivityListOut(Schema):
    """Schema for listing activities (minimal fields)."""

    public_id: str
    name: str
    date: datetime
    season: SeasonRef

    @staticmethod
    def resolve_season(obj):
        return obj.season


class ActivityOut(Schema):
    """Schema for full activity details."""

    public_id: str
    name: str
    date: datetime
    venue: VenueRef | None
    season: SeasonRef
    coaches: list[CoachRef]
    athletes: list[AthleteRef]

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
        return list(obj.athletes.all())  # Note: uses corrected field name
