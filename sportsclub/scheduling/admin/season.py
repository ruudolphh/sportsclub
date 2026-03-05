# scheduling/admin/season.py
from django.contrib import admin

from scheduling.models.season import Season


@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    """Admin interface for Season model."""

    list_display = [
        "public_id",
        "name",
        "start_date",
        "end_date",
        "duration_days",
    ]
    list_display_links = ["public_id", "name"]
    search_fields = ["public_id", "name"]
    list_filter = ["start_date", "end_date"]
    list_per_page = 50
    ordering = ["-start_date"]
    save_on_top = True

    fieldsets = (
        (
            "Season information",
            {
                "fields": ("name", "start_date", "end_date"),
                "description": "Define the season period",
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

    @admin.display(description="Duration (days)")
    def duration_days(self, obj):
        """Calculate and display the season duration in days."""
        if obj.start_date and obj.end_date:
            delta = obj.end_date - obj.start_date
            return delta.days
        return "-"
