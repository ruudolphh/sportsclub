# scheduling/api/seasons.py
from django.shortcuts import get_object_or_404
from ninja import Router

from scheduling.models import Season
from scheduling.schemas import (
    SeasonIn,
    SeasonListOut,
    SeasonOut,
    SeasonPatch,
)

router = Router(tags=["seasons"])


@router.get("/seasons", response=list[SeasonListOut])
def list_seasons(request):
    """List all seasons."""
    return Season.objects.all()


@router.get("/seasons/{public_id}", response=SeasonOut)
def get_season(request, public_id: str):
    """Get a single season by public ID."""
    return get_object_or_404(Season, public_id=public_id)


@router.post("/seasons", response={201: SeasonOut})
def create_season(request, payload: SeasonIn):
    """Create a new season."""
    season = Season.objects.create(**payload.model_dump())
    return 201, season


@router.put("/seasons/{public_id}", response=SeasonOut)
def update_season(request, public_id: str, payload: SeasonIn):
    """Fully update a season."""
    season = get_object_or_404(Season, public_id=public_id)
    for attr, value in payload.model_dump().items():
        setattr(season, attr, value)
    season.save()
    return season


@router.patch("/seasons/{public_id}", response=SeasonOut)
def partial_update_season(request, public_id: str, payload: SeasonPatch):
    """Partially update a season."""
    season = get_object_or_404(Season, public_id=public_id)
    for attr, value in payload.model_dump(exclude_unset=True).items():
        setattr(season, attr, value)
    season.save()
    return season


@router.delete("/seasons/{public_id}", response={204: None})
def delete_season(request, public_id: str):
    """Delete a season."""
    season = get_object_or_404(Season, public_id=public_id)
    season.delete()
    return 204, None
