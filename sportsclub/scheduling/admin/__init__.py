# scheduling/admin/__init__.py
from scheduling.admin.competition import CompetitionAdmin
from scheduling.admin.season import SeasonAdmin
from scheduling.admin.training import TrainingAdmin

__all__ = ["SeasonAdmin", "CompetitionAdmin", "TrainingAdmin"]
