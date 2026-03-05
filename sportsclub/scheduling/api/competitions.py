# scheduling/api/competitions.py
from django.shortcuts import get_object_or_404
from inventory.models import Venue
from ninja import Router
from people.models import Athlete, Coach

from scheduling.models import Competition, Season
from scheduling.schemas import (
    CompetitionIn,
    CompetitionListOut,
    CompetitionOut,
    CompetitionPatch,
)

router = Router(tags=["competitions"])


def _get_competition_queryset():
    """Return optimized queryset for competitions."""
    return Competition.objects.select_related("venue", "season").prefetch_related(
        "coaches", "athletes"
    )


def _process_competition_payload(payload, exclude_unset=False):
    """Process payload and return data dict with resolved foreign keys."""
    if exclude_unset:
        data = payload.model_dump(exclude_unset=True)
    else:
        data = payload.model_dump()

    # Handle score serialization
    if "score" in data and data["score"] is not None:
        data["score"] = (
            data["score"].model_dump()
            if hasattr(data["score"], "model_dump")
            else data["score"]
        )

    # Extract relationship fields
    venue_public_id = data.pop("venue_public_id", None)
    season_public_id = data.pop("season_public_id", None)
    coach_public_ids = data.pop("coach_public_ids", None)
    athlete_public_ids = data.pop("athlete_public_ids", None)

    return data, venue_public_id, season_public_id, coach_public_ids, athlete_public_ids


@router.get("/competitions", response=list[CompetitionListOut])
def list_competitions(request):
    """List all competitions."""
    return _get_competition_queryset()


@router.get("/competitions/{public_id}", response=CompetitionOut)
def get_competition(request, public_id: str):
    """Get a single competition by public ID."""
    return get_object_or_404(_get_competition_queryset(), public_id=public_id)


@router.post("/competitions", response={201: CompetitionOut})
def create_competition(request, payload: CompetitionIn):
    """Create a new competition."""
    data, venue_public_id, season_public_id, coach_public_ids, athlete_public_ids = (
        _process_competition_payload(payload)
    )

    # Resolve foreign keys
    if venue_public_id:
        data["venue"] = get_object_or_404(Venue, public_id=venue_public_id)
    data["season"] = get_object_or_404(Season, public_id=season_public_id)

    # Create competition
    competition = Competition.objects.create(**data)

    # Set ManyToMany relationships
    if coach_public_ids:
        coaches = Coach.objects.filter(public_id__in=coach_public_ids)
        competition.coaches.set(coaches)
    if athlete_public_ids:
        athletes = Athlete.objects.filter(public_id__in=athlete_public_ids)
        competition.athletes.set(athletes)

    return 201, competition


@router.put("/competitions/{public_id}", response=CompetitionOut)
def update_competition(request, public_id: str, payload: CompetitionIn):
    """Fully update a competition."""
    competition = get_object_or_404(Competition, public_id=public_id)

    data, venue_public_id, season_public_id, coach_public_ids, athlete_public_ids = (
        _process_competition_payload(payload)
    )

    # Resolve foreign keys
    if venue_public_id:
        data["venue"] = get_object_or_404(Venue, public_id=venue_public_id)
    else:
        data["venue"] = None
    data["season"] = get_object_or_404(Season, public_id=season_public_id)

    # Update fields
    for attr, value in data.items():
        setattr(competition, attr, value)
    competition.save()

    # Update ManyToMany relationships
    coaches = (
        Coach.objects.filter(public_id__in=coach_public_ids) if coach_public_ids else []
    )
    competition.coaches.set(coaches)
    athletes = (
        Athlete.objects.filter(public_id__in=athlete_public_ids)
        if athlete_public_ids
        else []
    )
    competition.athletes.set(athletes)

    return competition


@router.patch("/competitions/{public_id}", response=CompetitionOut)
def partial_update_competition(request, public_id: str, payload: CompetitionPatch):
    """Partially update a competition."""
    competition = get_object_or_404(Competition, public_id=public_id)

    data, venue_public_id, season_public_id, coach_public_ids, athlete_public_ids = (
        _process_competition_payload(payload, exclude_unset=True)
    )

    # Handle venue if provided
    if "venue_public_id" in payload.model_dump(exclude_unset=True):
        if venue_public_id:
            competition.venue = get_object_or_404(Venue, public_id=venue_public_id)
        else:
            competition.venue = None

    # Handle season if provided
    if season_public_id is not None:
        competition.season = get_object_or_404(Season, public_id=season_public_id)

    # Update scalar fields
    for attr, value in data.items():
        setattr(competition, attr, value)
    competition.save()

    # Update ManyToMany if provided
    if coach_public_ids is not None:
        coaches = Coach.objects.filter(public_id__in=coach_public_ids)
        competition.coaches.set(coaches)
    if athlete_public_ids is not None:
        athletes = Athlete.objects.filter(public_id__in=athlete_public_ids)
        competition.athletes.set(athletes)

    return competition


@router.delete("/competitions/{public_id}", response={204: None})
def delete_competition(request, public_id: str):
    """Delete a competition."""
    competition = get_object_or_404(Competition, public_id=public_id)
    competition.delete()
    return 204, None
