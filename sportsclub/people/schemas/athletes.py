# people/schemas/athletes.py
from datetime import date

from core.schemas import AddressOut
from ninja import Field, Schema
from pydantic import EmailStr

from people.schemas.common import PersonRef


class AthleteRef(PersonRef):
    """Reference to an athlete, for embedding in related resources."""

    jersey_number: int | None


class AthleteIn(Schema):
    """Schema for creating and fully updating an athlete (POST, PUT)."""

    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: str = Field("", max_length=20)
    date_of_birth: date | None = None
    address_public_id: str | None = None
    height: float | None = Field(
        None,
        gt=0,
        description="Height in centimeters",
        json_schema_extra={"example": 175.5},
    )
    weight: float | None = Field(
        None,
        gt=0,
        description="Weight in kilograms",
        json_schema_extra={"example": 70.0},
    )
    jersey_number: int | None = None


class AthletePatch(Schema):
    """Schema for partially updating an athlete (PATCH). All fields optional."""

    first_name: str | None = Field(None, min_length=1, max_length=100)
    last_name: str | None = Field(None, min_length=1, max_length=100)
    email: EmailStr | None = None
    phone: str | None = Field(None, max_length=20)
    date_of_birth: date | None = None
    address_public_id: str | None = None
    height: float | None = Field(
        None,
        gt=0,
        description="Height in centimeters",
    )
    weight: float | None = Field(
        None,
        gt=0,
        description="Weight in kilograms",
    )
    jersey_number: int | None = None


class AthleteListOut(Schema):
    """Schema for listing athletes (minimal fields)."""

    public_id: str
    first_name: str
    last_name: str
    jersey_number: int | None


class AthleteOut(Schema):
    """Schema for full athlete details."""

    public_id: str
    first_name: str
    last_name: str
    email: str
    phone: str
    date_of_birth: date | None
    address: AddressOut | None
    height: float | None
    weight: float | None
    jersey_number: int | None

    @staticmethod
    def resolve_address(obj):
        return obj.address if obj.address else None
