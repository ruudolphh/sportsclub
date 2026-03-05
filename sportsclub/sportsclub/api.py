# sportsclub/api.py
from core.api import router as core_router
from django.db import IntegrityError
from django.http import Http404
from inventory.api import router as inventory_router
from ninja import NinjaAPI
from ninja.errors import ValidationError
from people.api import router as people_router
from scheduling.api import router as scheduling_router

api = NinjaAPI(
    title="Athletics Sports Club API",
    version="1.0.0",
    description="API for managing athletic sports clubs",
    docs_url="/docs",  # Swagger UI at /api/v1/docs
    openapi_url="/openapi.json",  # OpenAPI spec at /api/v1/openapi.json
    # Unique ID to prevent "multiple NinjaAPIs" conflicts during test discovery
    urls_namespace="sportsclub_api",
)


@api.exception_handler(IntegrityError)
def handle_integrity_error(request, exc):
    """Handle database integrity errors (e.g., duplicate email)."""
    # We should return generic messages, e.g.,
    # "Unable to complete registration" or "Invalid credentials".
    # It is a trade-off between developer experience and security.
    return api.create_response(
        request,
        {"detail": "A record with this data already exists."},
        status=409,  # Conflict
    )


# Exception Handlers
@api.exception_handler(Http404)
def handle_not_found(request, exc):
    """Handle 404 errors with consistent JSON response."""
    return api.create_response(
        request,
        {"detail": "Resource not found"},
        status=404,
    )


@api.exception_handler(ValidationError)
def handle_validation_error(request, exc):
    """Handle validation errors with detailed error messages."""
    return api.create_response(
        request,
        {"detail": exc.errors},
        status=422,
    )


# Register app routers
api.add_router("/core", core_router)
api.add_router("/inventory", inventory_router)
api.add_router("/people", people_router)
api.add_router("/scheduling", scheduling_router)
