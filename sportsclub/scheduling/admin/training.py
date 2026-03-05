# scheduling/admin/training.py
from django.contrib import admin

from scheduling.models.training import Training


@admin.register(Training)
class TrainingAdmin(admin.ModelAdmin):
    """Admin interface for Training model."""

    list_display = [
        "public_id",
        "name",
        "date",
        "venue",
        "season",
        "focus",
        "athlete_count",
    ]
    list_display_links = ["public_id", "name"]
    search_fields = [
        "public_id",
        "name",
        "focus",
        "venue__name",
        "season__name",
    ]
    list_filter = ["season", "venue", "focus", "date"]
    list_per_page = 50
    ordering = ["-date"]
    save_on_top = True

    # Adds date-based drill-down navigation at the top of the list view
    date_hierarchy = "date"

    fieldsets = (
        (
            "Training information",
            {
                "fields": ("name", "date", "venue", "season", "focus"),
                "description": "Basic training session details",
            },
        ),
        (
            "Participants",
            {
                "fields": ("coaches", "athletes"),
                "description": "Assigned coaches and participating athletes",
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

    # Searchable dropdowns for foreign key fields, which requires `search_fields`
    # on the related model's admin.
    autocomplete_fields = ["venue", "season"]

    # Provides a nice dual-list widget for ManyToMany fields
    filter_horizontal = ["coaches", "athletes"]

    @admin.display(description="Athletes")
    def athlete_count(self, obj):
        """Display the number of participating athletes."""
        return obj.athletes.count()
