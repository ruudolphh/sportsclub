# inventory/api.py
from core.models import Address
from django.shortcuts import get_object_or_404
from ninja import Router

from inventory.models import Venue
from inventory.schemas import VenueIn, VenueListOut, VenueOut, VenuePatch

router = Router()


@router.get("/venues", response=list[VenueListOut], tags=["Venues"])
def list_venues(request):
    """
    List all venues.

    Returns a simplified view of all venues with essential fields.
    """
    return Venue.objects.select_related("address").all()


@router.get("/venues/{public_id}", response=VenueOut, tags=["Venues"])
def get_venue(request, public_id: str):
    """
    Get a single venue by its public ID.

    Args:
        public_id: The unique public identifier for the venue

    Returns:
        Complete venue details including address
    """
    venue = get_object_or_404(
        Venue.objects.select_related("address"), public_id=public_id
    )
    return venue


@router.post("/venues", response={201: VenueOut}, tags=["Venues"])
def create_venue(request, payload: VenueIn):
    """
    Create a new venue.

    Args:
        payload: Venue data including optional address_public_id

    Returns:
        The newly created venue
    """
    data = payload.model_dump(exclude={"address_public_id"})

    if payload.address_public_id:
        address = get_object_or_404(Address, public_id=payload.address_public_id)
        data["address"] = address

    venue = Venue.objects.create(**data)
    return 201, venue


@router.put("/venues/{public_id}", response=VenueOut, tags=["Venues"])
def update_venue(request, public_id: str, payload: VenueIn):
    """
    Fully update an existing venue (all fields replaced).

    Args:
        public_id: The unique public identifier for the venue
        payload: Complete venue data

    Returns:
        The updated venue
    """
    venue = get_object_or_404(Venue, public_id=public_id)
    data = payload.model_dump(exclude={"address_public_id"})

    if payload.address_public_id:
        address = get_object_or_404(Address, public_id=payload.address_public_id)
        data["address"] = address
    else:
        data["address"] = None

    for attr, value in data.items():
        setattr(venue, attr, value)

    venue.save()
    return venue


@router.patch("/venues/{public_id}", response=VenueOut, tags=["Venues"])
def partial_update_venue(request, public_id: str, payload: VenuePatch):
    """
    Partially update an existing venue (only provided fields updated).

    Args:
        public_id: The unique public identifier for the venue
        payload: Partial venue data

    Returns:
        The updated venue
    """
    venue = get_object_or_404(Venue, public_id=public_id)
    data = payload.model_dump(exclude_unset=True)

    # Handle address separately
    if "address_public_id" in data:
        address_public_id = data.pop("address_public_id")
        if address_public_id:
            venue.address = get_object_or_404(Address, public_id=address_public_id)
        else:
            venue.address = None

    for attr, value in data.items():
        setattr(venue, attr, value)

    venue.save()
    return venue


@router.delete("/venues/{public_id}", response={204: None}, tags=["Venues"])
def delete_venue(request, public_id: str):
    """
    Permanently delete a venue.

    Args:
        public_id: The unique public identifier for the venue

    Returns:
        204 No Content on successful deletion
    """
    venue = get_object_or_404(Venue, public_id=public_id)
    venue.delete()
    return 204, None
