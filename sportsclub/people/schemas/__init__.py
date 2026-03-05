# people/schemas/__init__.py
from people.schemas.athletes import (
    AthleteIn,
    AthleteListOut,
    AthleteOut,
    AthletePatch,
    AthleteRef,
)
from people.schemas.coaches import (
    CoachIn,
    CoachListOut,
    CoachOut,
    CoachPatch,
    CoachRef,
)
from people.schemas.common import PersonRef

__all__ = [
    "PersonRef",
    "AthleteIn",
    "AthleteListOut",
    "AthleteOut",
    "AthletePatch",
    "AthleteRef",
    "CoachIn",
    "CoachListOut",
    "CoachOut",
    "CoachPatch",
    "CoachRef",
]
