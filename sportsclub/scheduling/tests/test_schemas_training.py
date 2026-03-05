# scheduling/tests/test_schemas_training.py
from django.test import TestCase
from pydantic import ValidationError

from scheduling.schemas import (
    TrainingIn,
    TrainingPatch,
)


class TrainingInSchemaTest(TestCase):
    """Test TrainingIn schema validation."""

    def test_valid_full_training(self):
        """Test validation with all fields."""
        data = {
            "name": "Sprint Drills",
            "date": "2025-03-10T09:00:00Z",
            "venue_public_id": "venue123",
            "season_public_id": "season123",
            "coach_public_ids": ["coach1"],
            "athlete_public_ids": ["athlete1", "athlete2"],
            "focus": "Explosive starts",
        }
        schema = TrainingIn(**data)
        self.assertEqual(schema.name, "Sprint Drills")
        self.assertEqual(schema.focus, "Explosive starts")

    def test_valid_minimal_training(self):
        """Test validation with only required fields."""
        data = {
            "name": "Sprint Drills",
            "date": "2025-03-10T09:00:00Z",
            "season_public_id": "season123",
        }
        schema = TrainingIn(**data)
        self.assertEqual(schema.name, "Sprint Drills")
        self.assertIsNone(schema.venue_public_id)
        self.assertEqual(schema.focus, "")

    def test_missing_required_name(self):
        """Test that missing name raises validation error."""
        data = {
            "date": "2025-03-10T09:00:00Z",
            "season_public_id": "season123",
        }
        with self.assertRaises(ValidationError) as context:
            TrainingIn(**data)
        self.assertIn("name", str(context.exception))

    def test_missing_required_season(self):
        """Test that missing season_public_id raises validation error."""
        data = {
            "name": "Sprint Drills",
            "date": "2025-03-10T09:00:00Z",
        }
        with self.assertRaises(ValidationError) as context:
            TrainingIn(**data)
        self.assertIn("season_public_id", str(context.exception))

    def test_focus_too_long(self):
        """Test that focus exceeding max_length raises error."""
        data = {
            "name": "Sprint Drills",
            "date": "2025-03-10T09:00:00Z",
            "season_public_id": "season123",
            "focus": "F" * 256,
        }
        with self.assertRaises(ValidationError) as context:
            TrainingIn(**data)
        self.assertIn("focus", str(context.exception))


class TrainingPatchSchemaTest(TestCase):
    """Test TrainingPatch schema for partial updates."""

    def test_all_fields_optional(self):
        """Test that all fields are optional for PATCH."""
        schema = TrainingPatch()
        self.assertIsNone(schema.name)
        self.assertIsNone(schema.focus)

    def test_exclude_unset_returns_only_provided_fields(self):
        """Test model_dump(exclude_unset=True) returns only provided fields."""
        schema = TrainingPatch(focus="Updated focus")
        data = schema.model_dump(exclude_unset=True)
        self.assertEqual(data, {"focus": "Updated focus"})
