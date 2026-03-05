# people/models/coach.py
from django.db import models

from people.models.person import Person


class CoachingCertification(models.TextChoices):
    """Coaching certifications in athletics in Spain."""

    TECNICO_DEPORTIVO_GRADO_MEDIO = (
        "tecnico_deportivo_grado_medio",
        "Técnico Deportivo en Atletismo",
    )
    TECNICO_DEPORTIVO_GRADO_SUPERIOR = (
        "tecnico_deportivo_grado_superior",
        "Técnico Deportivo Superior en Atletismo",
    )
    ENTRENADOR_NACIONAL = (
        "entrenador_nacional",
        "Entrenador Nacional de Atletismo (RFEA)",
    )
    ENTRENADOR_CLUB = "entrenador_club", "Entrenador de Club"
    NSCA_CPT = "nsca_cpt", "Entrenador Personal (NSCA-CPT)"


class Coach(Person):
    """People teaching sports."""

    certification = models.CharField(
        null=True,
        blank=True,
        max_length=50,
        choices=CoachingCertification.choices,
    )
