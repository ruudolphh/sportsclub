# scheduling/tests/test_schemas_season.py
from datetime import date

from django.test import TestCase
from pydantic import ValidationError

from scheduling.models import Season
from scheduling.schemas import (
    SeasonIn,
    SeasonOut,
    SeasonPatch,
    SeasonRef,
)


class SeasonInSchemaTest(TestCase):
    """Test SeasonIn schema validation."""

    def test_valid_season(self):
        """Test validation with all fields."""
        data = {
            "name": "2024-2025 Season",
            "start_date": "2024-09-01",
            "end_date": "2025-06-30",
        }
        schema = SeasonIn(**data)
        self.assertEqual(schema.name, "2024-2025 Season")
        self.assertEqual(schema.start_date, date(2024, 9, 1))
        self.assertEqual(schema.end_date, date(2025, 6, 30))

    def test_missing_required_name(self):
        """Test that missing name raises validation error."""
        data = {
            "start_date": "2024-09-01",
            "end_date": "2025-06-30",
        }
        with self.assertRaises(ValidationError) as context:
            SeasonIn(**data)
        self.assertIn("name", str(context.exception))

    def test_missing_required_start_date(self):
        """Test that missing start_date raises validation error."""
        data = {
            "name": "2024-2025 Season",
            "end_date": "2025-06-30",
        }
        with self.assertRaises(ValidationError) as context:
            SeasonIn(**data)
        self.assertIn("start_date", str(context.exception))

    def test_missing_required_end_date(self):
        """Test that missing end_date raises validation error."""
        data = {
            "name": "2024-2025 Season",
            "start_date": "2024-09-01",
        }
        with self.assertRaises(ValidationError) as context:
            SeasonIn(**data)
        self.assertIn("end_date", str(context.exception))

    def test_name_too_long(self):
        """Test that name exceeding max_length raises error."""
        data = {
            "name": "S" * 101,
            "start_date": "2024-09-01",
            "end_date": "2025-06-30",
        }
        with self.assertRaises(ValidationError) as context:
            SeasonIn(**data)
        self.assertIn("name", str(context.exception))


class SeasonPatchSchemaTest(TestCase):
    """Test SeasonPatch schema for partial updates."""

    def test_all_fields_optional(self):
        """Test that all fields are optional for PATCH."""
        schema = SeasonPatch()
        self.assertIsNone(schema.name)
        self.assertIsNone(schema.start_date)
        self.assertIsNone(schema.end_date)

    def test_exclude_unset_returns_only_provided_fields(self):
        """Test model_dump(exclude_unset=True) returns only provided fields."""
        schema = SeasonPatch(name="Updated Season")
        data = schema.model_dump(exclude_unset=True)
        self.assertEqual(data, {"name": "Updated Season"})


class SeasonRefSchemaTest(TestCase):
    """Test SeasonRef schema."""

    def test_season_ref_fields(self):
        """Test SeasonRef has expected fields."""
        schema = SeasonRef(public_id="abc123", name="2024-2025 Season")
        self.assertEqual(schema.public_id, "abc123")
        self.assertEqual(schema.name, "2024-2025 Season")


class SeasonOutSchemaTest(TestCase):
    """Test SeasonOut schema serialization."""

    def test_serialize_season(self):
        """Test serializing Season model to SeasonOut schema."""
        season = Season.objects.create(
            name="2024-2025 Season",
            start_date=date(2024, 9, 1),
            end_date=date(2025, 6, 30),
        )
        schema = SeasonOut.from_orm(season)
        self.assertEqual(schema.name, "2024-2025 Season")
        self.assertEqual(schema.start_date, date(2024, 9, 1))
        self.assertIsNotNone(schema.public_id)
