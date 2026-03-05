# people/api.py
import logging

from core.models import Address
from django.shortcuts import get_object_or_404
from ninja import Router

from people.models import Athlete
from people.schemas import (
    AthleteIn,
    AthleteListOut,
    AthleteOut,
    AthletePatch,
)

logger = logging.getLogger(__name__)
router = Router(tags=["people"])


# Athlete endpoints
@router.get("/athletes", response=list[AthleteListOut])
def list_athletes(request):
    """List all athletes."""
    return Athlete.objects.all()


@router.get("/athletes/{public_id}", response=AthleteOut)
def get_athlete(request, public_id: str):
    """Get a single athlete by public ID."""
    athlete = get_object_or_404(
        Athlete.objects.select_related("address"), public_id=public_id
    )
    return athlete


@router.post("/athletes", response={201: AthleteOut})
def create_athlete(request, payload: AthleteIn):
    """Create a new athlete."""
    data = payload.model_dump(exclude={"address_public_id"})
    if payload.address_public_id:
        data["address"] = get_object_or_404(
            Address, public_id=payload.address_public_id
        )
    athlete = Athlete.objects.create(**data)
    logger.info(f"Created athlete with public id {athlete.public_id}: {athlete}")
    return 201, athlete


@router.put("/athletes/{public_id}", response=AthleteOut)
def update_athlete(request, public_id: str, payload: AthleteIn):
    """Fully update an athlete."""
    athlete = get_object_or_404(Athlete, public_id=public_id)
    data = payload.model_dump(exclude={"address_public_id"})
    if payload.address_public_id:
        data["address"] = get_object_or_404(
            Address, public_id=payload.address_public_id
        )
    else:
        data["address"] = None
    for attr, value in data.items():
        setattr(athlete, attr, value)
    athlete.save()
    return athlete


@router.patch("/athletes/{public_id}", response=AthleteOut)
def partial_update_athlete(request, public_id: str, payload: AthletePatch):
    """Partially update an athlete."""
    athlete = get_object_or_404(Athlete, public_id=public_id)
    data = payload.model_dump(exclude_unset=True)
    if "address_public_id" in data:
        address_public_id = data.pop("address_public_id")
        athlete.address = (
            get_object_or_404(Address, public_id=address_public_id)
            if address_public_id
            else None
        )
    for attr, value in data.items():
        setattr(athlete, attr, value)
    athlete.save()
    return athlete


@router.delete("/athletes/{public_id}", response={204: None})
def delete_athlete(request, public_id: str):
    """Delete an athlete."""
    athlete = get_object_or_404(Athlete, public_id=public_id)
    athlete.delete()
    return 204, None
