# people/models/__init__.py
"""Models for the people app."""

from .athlete import Athlete
from .coach import Coach, CoachingCertification
from .person import Person

__all__ = [
    "Athlete",
    "Coach",
    "CoachingCertification",
    "Person",
]
