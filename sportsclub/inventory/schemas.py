# inventory/schemas.py
from core.schemas import AddressOut
from ninja import Field, Schema

from inventory.models import VenueType


class VenueRef(Schema):
    """Reference to a venue, for embedding in related resources."""

    public_id: str
    name: str


class VenueIn(Schema):
    """Schema for creating and fully updating a venue (POST, PUT)."""

    name: str = Field(..., min_length=1, max_length=200)
    venue_type: VenueType = Field(default=VenueType.FIELD)
    capacity: int | None = Field(None, ge=0)
    address_public_id: str | None = None
    indoor: bool = False


class VenuePatch(Schema):
    """Schema for partially updating a venue (PATCH). All fields optional."""

    name: str | None = Field(None, min_length=1, max_length=200)
    venue_type: VenueType | None = None
    capacity: int | None = Field(None, ge=0)
    address_public_id: str | None = None
    indoor: bool | None = None


class VenueListOut(Schema):
    """Simplified schema for listing venues."""

    public_id: str
    name: str
    venue_type: VenueType
    indoor: bool


class VenueOut(Schema):
    """Schema for full venue details."""

    public_id: str
    name: str
    venue_type: VenueType
    capacity: int | None
    address: AddressOut | None
    indoor: bool

    @staticmethod
    def resolve_address(obj):
        return obj.address if obj.address else None
