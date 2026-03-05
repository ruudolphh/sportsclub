# core/admin.py
from django.contrib import admin

from .models import Address


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    """Admin interface for Address model."""

    # Which columns appear in the table
    list_display = ["public_id", "line1", "postal_code", "city", "country"]

    # Which columns are clickable links to the edit page
    list_display_links = ["public_id", "line1"]

    # Which fields the search box queries
    search_fields = [
        "public_id",
        "line1",
        "line2",
        "postal_code",
        "city",
        "state",
        "country",
    ]

    # Adds filter dropdowns in the sidebar
    list_filter = ["country", "state", "city"]

    # Pagination: 50 records per page
    list_per_page = 50

    # Default sort order
    ordering = ["country", "city", "line1"]

    # Adds save buttons at the top of the form, not just the bottom
    save_on_top = True

    # Groups fields into collapsible sections with headers and descriptions.
    # The 'classes': ('collapse',) makes "System information" collapsed by default.
    fieldsets = (
        (
            "Address information",
            {"fields": ("line1", "line2"), "description": "Primary address details"},
        ),
        (
            "Location",
            {
                "fields": ("postal_code", "city", "state", "country"),
                "description": "Geographic location details",
            },
        ),
        (
            "System information",
            {
                "fields": ("id", "public_id", "formatted_address"),
                "classes": ("collapse",),
                "description": "Read-only system fields for debugging",
            },
        ),
    )

    # These fields are displayed but cannot be edited
    readonly_fields = ["id", "public_id", "formatted_address"]

    # Adds a computed field showing the address as it would appear when converted to
    # string (via the model's `__str__` method).
    # The `short_description` attrbite sets its label in the admin.
    def formatted_address(self, obj):
        """Display how the address will be formatted in the system."""
        return str(obj)

    formatted_address.short_description = "Formatted display"
