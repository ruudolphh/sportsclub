# scheduling/api/__init__.py
from ninja import Router

from scheduling.api.competitions import router as competitions_router
from scheduling.api.seasons import router as seasons_router
from scheduling.api.trainings import router as trainings_router

router = Router(tags=["scheduling"])
router.add_router("", seasons_router)
router.add_router("", competitions_router)
router.add_router("", trainings_router)
