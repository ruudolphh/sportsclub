# scheduling/schemas/season.py
from datetime import date

from ninja import Field, Schema


class SeasonRef(Schema):
    """Reference to a season, for embedding in related resources."""

    public_id: str
    name: str


class SeasonIn(Schema):
    """Schema for creating and fully updating a season (POST, PUT)."""

    name: str = Field(..., min_length=1, max_length=100)
    start_date: date
    end_date: date


class SeasonPatch(Schema):
    """Schema for partially updating a season (PATCH). All fields optional."""

    name: str | None = Field(None, min_length=1, max_length=100)
    start_date: date | None = None
    end_date: date | None = None


class SeasonListOut(Schema):
    """Schema for listing seasons (minimal fields)."""

    public_id: str
    name: str
    start_date: date
    end_date: date


class SeasonOut(Schema):
    """Schema for full season details."""

    public_id: str
    name: str
    start_date: date
    end_date: date
