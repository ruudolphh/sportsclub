# core/api.py
from django.shortcuts import get_object_or_404
from ninja import Router

from core.models.address import Address

from .schemas import (
    AddressIn,
    AddressListOut,
    AddressOut,
    AddressPatch,
    ErrorResponse,
    ValidationErrorResponse,
)

router = Router()


# XXX: Rate limit example to be expanded in the future
# @ratelimit(key="ip", rate="100/h")
@router.get("/addresses", response=list[AddressListOut], tags=["Addresses"])
def list_addresses(request):
    """
    List all addresses.

    Returns a simplified view of all addresses with only essential fields.
    """
    addresses = Address.objects.all()
    return addresses


@router.get(
    "/addresses/{public_id}",
    response={200: AddressOut, 404: ErrorResponse},
    tags=["Addresses"],
)
def get_address(request, public_id: str):
    """
    Get a single address by its public ID.

    Args:
        public_id: The unique public identifier for the address

    Returns:
        Complete address details including all fields
    """
    address = get_object_or_404(Address, public_id=public_id)
    return address


"""
400 is for syntactically incorrect requests,
409 is for conflicts with the resource's current state,
and 422 is for valid requests that fail semantic or business rule validation.

Pydantic raises 422 automatically. We raise 400 and 409 manually. Example:

@router.post("/competitions", response={201: CompetitionOut})
def create_competition(request, payload: CompetitionIn):
    # 404 — handled by get_object_or_404
    season = get_object_or_404(Season, public_id=payload.season_public_id)

    # 409 — duplicate/conflict (you check and raise)
    if Competition.objects.filter(name=payload.name, season=season).exists():
        raise HttpError(409, "A competition with this name already exists in this
        season")

    # 400 — business logic validation (you check and raise)
    if payload.date < season.start_date or payload.date > season.end_date:
        raise HttpError(400, "Competition date must fall within the season dates")

    competition = Competition.objects.create(...)
    return 201, competition
"""


@router.post(
    "/addresses",
    response={
        201: AddressOut,
        400: ValidationErrorResponse,
        404: ErrorResponse,
        422: ValidationErrorResponse,
    },
    tags=["Addresses"],
)
def create_address(request, payload: AddressIn):
    """
    Create a new address.

    Args:
        payload: Address data including line1 (required) and optional fields

    Returns:
        The newly created address with generated public_id
    """
    address = Address.objects.create(**payload.model_dump())
    return 201, address


@router.put("/addresses/{public_id}", response=AddressOut, tags=["Addresses"])
def update_address(request, public_id: str, payload: AddressIn):
    """
    Fully update an existing address (all fields replaced).

    Args:
        public_id: The unique public identifier for the address
        payload: Complete address data (all fields will be updated)

    Returns:
        The updated address
    """
    address = get_object_or_404(Address, public_id=public_id)

    for attr, value in payload.model_dump().items():
        setattr(address, attr, value)

    address.save()
    return address


@router.patch("/addresses/{public_id}", response=AddressOut, tags=["Addresses"])
def partial_update_address(request, public_id: str, payload: AddressPatch):
    """
    Partially update an existing address (only provided fields updated).

    Args:
        public_id: The unique public identifier for the address
        payload: Partial address data (only provided fields will be updated)

    Returns:
        The updated address
    """
    address = get_object_or_404(Address, public_id=public_id)

    # Only update fields that were actually provided
    for attr, value in payload.model_dump(exclude_unset=True).items():
        setattr(address, attr, value)

    address.save()
    return address


@router.delete("/addresses/{public_id}", response={204: None}, tags=["Addresses"])
def delete_address(request, public_id: str):
    """
    Permanently delete an address.

    Warning: This action cannot be undone. Ensure no entities (venues, athletes)
    are referencing this address before deletion.

    Args:
        public_id: The unique public identifier for the address

    Returns:
        204 No Content on successful deletion
    """
    address = get_object_or_404(Address, public_id=public_id)
    address.delete()
    return 204, None
