# scheduling/admin/competition.py
from django.contrib import admin

from scheduling.models.competition import Competition


@admin.register(Competition)
class CompetitionAdmin(admin.ModelAdmin):
    """Admin interface for Competition model."""

    list_display = [
        "public_id",
        "name",
        "date",
        "venue",
        "season",
        "athlete_count",
        "has_score",
    ]
    list_display_links = ["public_id", "name"]
    search_fields = [
        "public_id",
        "name",
        "venue__name",
        "season__name",
    ]
    list_filter = ["season", "venue", "date"]
    list_per_page = 50
    ordering = ["-date"]
    save_on_top = True
    date_hierarchy = "date"

    fieldsets = (
        (
            "Competition information",
            {
                "fields": ("name", "date", "venue", "season"),
                "description": "Basic competition details",
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
            "Results",
            {
                "fields": ("score",),
                "description": "Competition scores and results (JSON format)",
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
    autocomplete_fields = ["venue", "season"]
    filter_horizontal = ["coaches", "athletes"]

    @admin.display(description="Athletes")
    def athlete_count(self, obj):
        """Display the number of participating athletes."""
        return obj.athletes.count()

    # `boolean=True` shows a checkbox icon instead of True/False
    @admin.display(description="Scored", boolean=True)
    def has_score(self, obj):
        """Indicate whether the competition has scores recorded."""
        return obj.score is not None
