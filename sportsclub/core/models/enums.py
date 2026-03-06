# core/models/enums.py
from enum import StrEnum


class Discipline(StrEnum):
    """Athletic disciplines tracked in competitions."""

    SPRINTS = "sprints"
    LONG_DISTANCE = "long_distance"
    RELAYS = "relays"
    HIGH_JUMP = "high_jump"
    LONG_JUMP = "long_jump"
