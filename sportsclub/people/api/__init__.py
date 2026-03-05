# people/api/__init__.py
from ninja import Router

from people.api.athletes import router as athletes_router
from people.api.coaches import router as coaches_router

router = Router(tags=["people"])
router.add_router("", athletes_router)
router.add_router("", coaches_router)
