# scheduling/schemas/__init__.py
from scheduling.schemas.common import CompetitionScore, MedalCount
from scheduling.schemas.competition import (
    CompetitionIn,
    CompetitionListOut,
    CompetitionOut,
    CompetitionPatch,
)
from scheduling.schemas.season import (
    SeasonIn,
    SeasonListOut,
    SeasonOut,
    SeasonPatch,
    SeasonRef,
)
from scheduling.schemas.training import (
    TrainingIn,
    TrainingListOut,
    TrainingOut,
    TrainingPatch,
)

__all__ = [
    "CompetitionScore",
    "MedalCount",
    "SeasonIn",
    "SeasonListOut",
    "SeasonOut",
    "SeasonPatch",
    "SeasonRef",
    "CompetitionIn",
    "CompetitionListOut",
    "CompetitionOut",
    "CompetitionPatch",
    "TrainingIn",
    "TrainingListOut",
    "TrainingOut",
    "TrainingPatch",
]
