# scheduling/tests/test_models_season.py
from datetime import date

from django.test import TestCase

from scheduling.models import Season


class SeasonModelTest(TestCase):
    """Test suite for Season model."""

    def setUp(self):
        """Set up test data."""
        self.season = Season.objects.create(
            name="2024-2025 Season",
            start_date=date(2024, 9, 1),
            end_date=date(2025, 6, 30),
        )

    def test_create_season(self):
        """Test creating a season."""
        self.assertIsNotNone(self.season.pk)
        self.assertIsNotNone(self.season.public_id)

    def test_str_representation(self):
        """Test __str__ returns name."""
        self.assertEqual(str(self.season), "2024-2025 Season")

    def test_public_id_generated_automatically(self):
        """Test that public_id is auto-generated."""
        self.assertIsNotNone(self.season.public_id)
        self.assertGreater(len(self.season.public_id), 0)

    def test_public_id_is_unique(self):
        """Test that each season gets a unique public_id."""
        season2 = Season.objects.create(
            name="2025-2026 Season",
            start_date=date(2025, 9, 1),
            end_date=date(2026, 6, 30),
        )
        self.assertNotEqual(self.season.public_id, season2.public_id)

    def test_ordering_by_start_date_descending(self):
        """Test that seasons are ordered by start_date descending."""
        older_season = Season.objects.create(
            name="2023-2024 Season",
            start_date=date(2023, 9, 1),
            end_date=date(2024, 6, 30),
        )
        seasons = list(Season.objects.all())
        self.assertEqual(seasons[0], self.season)
        self.assertEqual(seasons[1], older_season)

    def test_auditory_fields_created(self):
        """Test that created_at and updated_at are set automatically."""
        self.assertIsNotNone(self.season.created_at)
        self.assertIsNotNone(self.season.updated_at)
