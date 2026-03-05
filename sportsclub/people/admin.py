# people/admin.py
from django.contrib import admin

from .models import Athlete, Coach


@admin.register(Coach)
class CoachAdmin(admin.ModelAdmin):
    """Admin interface for Coach model."""

    list_display = [
        "public_id",
        "full_name",
        "email",
        "certification",
        "get_city",
    ]
    list_display_links = ["public_id", "full_name"]
    search_fields = [
        "public_id",
        "first_name",
        "last_name",
        "email",
        "phone",
        "address__city",
    ]
    list_filter = ["certification", "address__country", "address__city"]
    list_per_page = 50
    ordering = ["last_name", "first_name"]
    save_on_top = True

    fieldsets = (
        (
            "Personal information",
            {
                "fields": ("first_name", "last_name", "date_of_birth"),
                "description": "Basic personal details",
            },
        ),
        (
            "Contact information",
            {
                "fields": ("email", "phone", "address"),
                "description": "How to reach this coach",
            },
        ),
        (
            "Professional information",
            {
                "fields": ("certification",),
                "description": "Coaching qualifications",
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
    autocomplete_fields = ["address"]

    @admin.display(description="Name")
    def full_name(self, obj):
        """Display full name."""
        return f"{obj.first_name} {obj.last_name}"

    @admin.display(description="City")
    def get_city(self, obj):
        """Display the city from the related address."""
        return obj.address.city if obj.address else "-"


@admin.register(Athlete)
class AthleteAdmin(admin.ModelAdmin):
    """Admin interface for Athlete model."""

    list_display = [
        "public_id",
        "full_name",
        "email",
        "jersey_number",
        "height",
        "weight",
        "get_city",
    ]
    list_display_links = ["public_id", "full_name"]
    search_fields = [
        "public_id",
        "first_name",
        "last_name",
        "email",
        "phone",
        "jersey_number",
        "address__city",
    ]
    list_filter = ["address__country", "address__city"]
    list_per_page = 50
    ordering = ["last_name", "first_name"]
    save_on_top = True

    fieldsets = (
        (
            "Personal information",
            {
                "fields": ("first_name", "last_name", "date_of_birth"),
                "description": "Basic personal details",
            },
        ),
        (
            "Contact information",
            {
                "fields": ("email", "phone", "address"),
                "description": "How to reach this athlete",
            },
        ),
        (
            "Athletic information",
            {
                "fields": ("jersey_number", "height", "weight"),
                "description": "Physical and team details",
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
    autocomplete_fields = ["address"]

    @admin.display(description="Name")
    def full_name(self, obj):
        """Display full name."""
        return f"{obj.first_name} {obj.last_name}"

    @admin.display(description="City")
    def get_city(self, obj):
        """Display the city from the related address."""
        return obj.address.city if obj.address else "-"
