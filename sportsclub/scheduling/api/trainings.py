# scheduling/api/trainings.py
from django.shortcuts import get_object_or_404
from inventory.models import Venue
from ninja import Router
from people.models import Athlete, Coach

from scheduling.models import Season, Training
from scheduling.schemas import (
    TrainingIn,
    TrainingListOut,
    TrainingOut,
    TrainingPatch,
)

router = Router(tags=["trainings"])


def _get_training_queryset():
    """Return optimized queryset for trainings."""
    return Training.objects.select_related("venue", "season").prefetch_related(
        "coaches", "athletes"
    )


@router.get("/trainings", response=list[TrainingListOut])
def list_trainings(request):
    """List all training sessions."""
    return _get_training_queryset()


@router.get("/trainings/{public_id}", response=TrainingOut)
def get_training(request, public_id: str):
    """Get a single training session by public ID."""
    return get_object_or_404(_get_training_queryset(), public_id=public_id)


@router.post("/trainings", response={201: TrainingOut})
def create_training(request, payload: TrainingIn):
    """Create a new training session."""
    data = payload.model_dump()

    # Extract relationship fields
    venue_public_id = data.pop("venue_public_id", None)
    season_public_id = data.pop("season_public_id")
    coach_public_ids = data.pop("coach_public_ids", [])
    athlete_public_ids = data.pop("athlete_public_ids", [])

    # Resolve foreign keys
    if venue_public_id:
        data["venue"] = get_object_or_404(Venue, public_id=venue_public_id)
    data["season"] = get_object_or_404(Season, public_id=season_public_id)

    # Create training
    training = Training.objects.create(**data)

    # Set ManyToMany relationships
    if coach_public_ids:
        coaches = Coach.objects.filter(public_id__in=coach_public_ids)
        training.coaches.set(coaches)
    if athlete_public_ids:
        athletes = Athlete.objects.filter(public_id__in=athlete_public_ids)
        training.athletes.set(athletes)

    return 201, training


@router.put("/trainings/{public_id}", response=TrainingOut)
def update_training(request, public_id: str, payload: TrainingIn):
    """Fully update a training session."""
    training = get_object_or_404(Training, public_id=public_id)
    data = payload.model_dump()

    # Extract relationship fields
    venue_public_id = data.pop("venue_public_id", None)
    season_public_id = data.pop("season_public_id")
    coach_public_ids = data.pop("coach_public_ids", [])
    athlete_public_ids = data.pop("athlete_public_ids", [])

    # Resolve foreign keys
    if venue_public_id:
        data["venue"] = get_object_or_404(Venue, public_id=venue_public_id)
    else:
        data["venue"] = None
    data["season"] = get_object_or_404(Season, public_id=season_public_id)

    # Update fields
    for attr, value in data.items():
        setattr(training, attr, value)
    training.save()

    # Update ManyToMany relationships
    coaches = Coach.objects.filter(public_id__in=coach_public_ids)
    training.coaches.set(coaches)
    athletes = Athlete.objects.filter(public_id__in=athlete_public_ids)
    training.athletes.set(athletes)

    return training


@router.patch("/trainings/{public_id}", response=TrainingOut)
def partial_update_training(request, public_id: str, payload: TrainingPatch):
    """Partially update a training session."""
    training = get_object_or_404(Training, public_id=public_id)
    data = payload.model_dump(exclude_unset=True)

    # Handle venue if provided
    if "venue_public_id" in data:
        venue_public_id = data.pop("venue_public_id")
        if venue_public_id:
            training.venue = get_object_or_404(Venue, public_id=venue_public_id)
        else:
            training.venue = None

    # Handle season if provided
    if "season_public_id" in data:
        season_public_id = data.pop("season_public_id")
        training.season = get_object_or_404(Season, public_id=season_public_id)

    # Handle ManyToMany if provided
    if "coach_public_ids" in data:
        coach_public_ids = data.pop("coach_public_ids")
        if coach_public_ids is not None:
            coaches = Coach.objects.filter(public_id__in=coach_public_ids)
            training.coaches.set(coaches)

    if "athlete_public_ids" in data:
        athlete_public_ids = data.pop("athlete_public_ids")
        if athlete_public_ids is not None:
            athletes = Athlete.objects.filter(public_id__in=athlete_public_ids)
            training.athletes.set(athletes)

    # Update remaining scalar fields
    for attr, value in data.items():
        setattr(training, attr, value)
    training.save()

    return training


@router.delete("/trainings/{public_id}", response={204: None})
def delete_training(request, public_id: str):
    """Delete a training session."""
    training = get_object_or_404(Training, public_id=public_id)
    training.delete()
    return 204, None
