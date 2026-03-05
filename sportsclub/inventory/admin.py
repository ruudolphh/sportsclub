# inventory/admin.py
from django.contrib import admin

from .models import Venue


@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    """Admin interface for Venue model."""

    list_display = ["public_id", "name", "get_city", "get_country"]
    list_display_links = ["public_id", "name"]
    search_fields = [
        "public_id",
        "name",
        "address__city",
        "address__country",
    ]
    list_filter = ["address__country", "address__city"]
    list_per_page = 50
    ordering = ["name"]
    save_on_top = True

    fieldsets = (
        (
            "Venue information",
            {
                "fields": ("name", "address"),
                "description": "Basic venue details",
            },
        ),
        (
            "System information",
            {
                "fields": ("id", "public_id", "created_at", "updated_at"),
                "classes": ("collapse",),
                "description": "Read-only system fields",
            },
        ),
    )

    readonly_fields = ["id", "public_id", "created_at", "updated_at"]

    # XXX: `autocomplete_fields`` requires the related model `Address`) to have
    # `search_fields` defined in its admin, which we already have. This gives a
    # searchable dropdown instead of loading all addresses.
    autocomplete_fields = ["address"]

    @admin.display(description="City")
    def get_city(self, obj):
        """Display the city from the related address."""
        return obj.address.city if obj.address else "-"

    @admin.display(description="Country")
    def get_country(self, obj):
        """Display the country from the related address."""
        return obj.address.country if obj.address else "-"
