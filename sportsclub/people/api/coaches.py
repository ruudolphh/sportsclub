# people/api/coaches.py
from core.models import Address
from django.shortcuts import get_object_or_404
from ninja import Router

from people.models import Coach
from people.schemas import (
    CoachIn,
    CoachListOut,
    CoachOut,
    CoachPatch,
)

router = Router(tags=["coaches"])


@router.get("/coaches", response=list[CoachListOut])
def list_coaches(request):
    """List all coaches."""
    return Coach.objects.all()


@router.get("/coaches/{public_id}", response=CoachOut)
def get_coach(request, public_id: str):
    """Get a single coach by public ID."""
    coach = get_object_or_404(
        Coach.objects.select_related("address"), public_id=public_id
    )
    return coach


@router.post("/coaches", response={201: CoachOut})
def create_coach(request, payload: CoachIn):
    """Create a new coach."""
    data = payload.model_dump(exclude={"address_public_id"})
    if payload.address_public_id:
        data["address"] = get_object_or_404(
            Address, public_id=payload.address_public_id
        )
    coach = Coach.objects.create(**data)
    return 201, coach


@router.put("/coaches/{public_id}", response=CoachOut)
def update_coach(request, public_id: str, payload: CoachIn):
    """Fully update a coach."""
    coach = get_object_or_404(Coach, public_id=public_id)
    data = payload.model_dump(exclude={"address_public_id"})
    if payload.address_public_id:
        data["address"] = get_object_or_404(
            Address, public_id=payload.address_public_id
        )
    else:
        data["address"] = None
    for attr, value in data.items():
        setattr(coach, attr, value)
    coach.save()
    return coach


@router.patch("/coaches/{public_id}", response=CoachOut)
def partial_update_coach(request, public_id: str, payload: CoachPatch):
    """Partially update a coach."""
    coach = get_object_or_404(Coach, public_id=public_id)
    data = payload.model_dump(exclude_unset=True)
    if "address_public_id" in data:
        address_public_id = data.pop("address_public_id")
        coach.address = (
            get_object_or_404(Address, public_id=address_public_id)
            if address_public_id
            else None
        )
    for attr, value in data.items():
        setattr(coach, attr, value)
    coach.save()
    return coach


@router.delete("/coaches/{public_id}", response={204: None})
def delete_coach(request, public_id: str):
    """Delete a coach."""
    coach = get_object_or_404(Coach, public_id=public_id)
    coach.delete()
    return 204, None
