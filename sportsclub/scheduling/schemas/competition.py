# scheduling/schemas/competition.py
from datetime import datetime

from inventory.schemas import VenueRef
from ninja import Field, Schema
from people.schemas import AthleteRef, CoachRef

from scheduling.schemas.common import CompetitionScore
from scheduling.schemas.season import SeasonRef


class CompetitionIn(Schema):
    """Schema for creating and fully updating a competition (POST, PUT)."""

    name: str = Field(..., min_length=1, max_length=255, description="Descriptive name")
    date: datetime = Field(..., description="Event date and time")
    venue_public_id: str | None = Field(
        default=None, description="The venue where it is taking place"
    )
    season_public_id: str = Field(..., description="Season the competition belongs to")
    coach_public_ids: list[str] = Field(
        default_factory=list, description="List of coaches attending the competition"
    )
    athlete_public_ids: list[str] = Field(
        default_factory=list, description="List of athletes attending the competition"
    )
    score: CompetitionScore | None = None


class CompetitionPatch(Schema):
    """Schema for partially updating a competition (PATCH). All fields optional."""

    name: str | None = Field(None, min_length=1, max_length=255)
    date: datetime | None = None
    venue_public_id: str | None = None
    season_public_id: str | None = None
    coach_public_ids: list[str] | None = None
    athlete_public_ids: list[str] | None = None
    score: CompetitionScore | None = None


class CompetitionListOut(Schema):
    """Schema for listing competitions (minimal fields)."""

    public_id: str
    name: str
    date: datetime
    season: SeasonRef

    @staticmethod
    def resolve_season(obj):
        return obj.season


class CompetitionOut(Schema):
    """Schema for full competition details."""

    public_id: str
    name: str
    date: datetime
    venue: VenueRef | None
    season: SeasonRef
    coaches: list[CoachRef]
    athletes: list[AthleteRef]
    score: CompetitionScore | None

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

    @staticmethod
    def resolve_score(obj):
        if obj.score:
            return CompetitionScore(**obj.score)
        return None
