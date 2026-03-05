# people/schemas/coaches.py
from datetime import date

from core.schemas import AddressOut
from ninja import Field, Schema
from pydantic import EmailStr

from people.models import CoachingCertification
from people.schemas.common import PersonRef


class CoachRef(PersonRef):
    """Reference to a coach, for embedding in related resources."""

    pass


class CoachIn(Schema):
    """Schema for creating and fully updating a coach (POST, PUT)."""

    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: str = Field("", max_length=20)
    date_of_birth: date | None = None
    address_public_id: str | None = None
    certification: CoachingCertification | None = None


class CoachPatch(Schema):
    """Schema for partially updating a coach (PATCH). All fields optional."""

    first_name: str | None = Field(None, min_length=1, max_length=100)
    last_name: str | None = Field(None, min_length=1, max_length=100)
    email: EmailStr | None = None
    phone: str | None = Field(None, max_length=20)
    date_of_birth: date | None = None
    address_public_id: str | None = None
    certification: CoachingCertification | None = None


class CoachListOut(Schema):
    """Schema for listing coaches (minimal fields)."""

    public_id: str
    first_name: str
    last_name: str
    certification: CoachingCertification | None


class CoachOut(Schema):
    """Schema for full coach details."""

    public_id: str
    first_name: str
    last_name: str
    email: str
    phone: str
    date_of_birth: date | None
    address: AddressOut | None
    certification: CoachingCertification | None

    @staticmethod
    def resolve_address(obj):
        return obj.address if obj.address else None
