# scheduling/tests/test_schemas_competition.py

from core.models.enums import Discipline
from django.test import TestCase
from pydantic import ValidationError

from scheduling.schemas import (
    CompetitionIn,
    CompetitionPatch,
)
from scheduling.schemas.common import CompetitionScore, MedalCount


class MedalCountSchemaTest(TestCase):
    """Test MedalCount schema validation."""

    def test_valid_medal_count(self):
        """Test validation with all fields."""
        schema = MedalCount(gold=2, silver=1, bronze=3)
        self.assertEqual(schema.gold, 2)
        self.assertEqual(schema.silver, 1)
        self.assertEqual(schema.bronze, 3)

    def test_default_values(self):
        """Test default values are zero."""
        schema = MedalCount()
        self.assertEqual(schema.gold, 0)
        self.assertEqual(schema.silver, 0)
        self.assertEqual(schema.bronze, 0)

    def test_negative_values_rejected(self):
        """Test that negative values raise validation error."""
        with self.assertRaises(ValidationError):
            MedalCount(gold=-1)


class CompetitionScoreSchemaTest(TestCase):
    """Test CompetitionScore schema validation."""

    def test_valid_score(self):
        """Test validation with valid results."""
        data = {
            "results": {
                "sprints": {"gold": 2, "silver": 1, "bronze": 0},
                "high_jump": {"gold": 1, "silver": 0, "bronze": 1},
            }
        }
        schema = CompetitionScore(**data)
        self.assertEqual(schema.results[Discipline.SPRINTS].gold, 2)
        self.assertEqual(schema.results[Discipline.HIGH_JUMP].gold, 1)

    def test_empty_results(self):
        """Test validation with empty results."""
        schema = CompetitionScore()
        self.assertEqual(schema.results, {})

    def test_invalid_discipline_rejected(self):
        """Test that invalid discipline raises validation error."""
        data = {
            "results": {"invalid_discipline": {"gold": 1, "silver": 0, "bronze": 0}}
        }
        with self.assertRaises(ValidationError):
            CompetitionScore(**data)

    def test_extra_fields_forbidden(self):
        """Test that extra fields are rejected."""
        data = {
            "results": {},
            "extra_field": "not allowed",
        }
        with self.assertRaises(ValidationError):
            CompetitionScore(**data)


class CompetitionInSchemaTest(TestCase):
    """Test CompetitionIn schema validation."""

    def test_valid_full_competition(self):
        """Test validation with all fields."""
        data = {
            "name": "Spring Championship",
            "date": "2025-04-15T10:00:00Z",
            "venue_public_id": "venue123",
            "season_public_id": "season123",
            "coach_public_ids": ["coach1", "coach2"],
            "athlete_public_ids": ["athlete1", "athlete2"],
            "score": {"results": {"sprints": {"gold": 2, "silver": 1, "bronze": 0}}},
        }
        schema = CompetitionIn(**data)
        self.assertEqual(schema.name, "Spring Championship")
        self.assertEqual(len(schema.coach_public_ids), 2)

    def test_valid_minimal_competition(self):
        """Test validation with only required fields."""
        data = {
            "name": "Spring Championship",
            "date": "2025-04-15T10:00:00Z",
            "season_public_id": "season123",
        }
        schema = CompetitionIn(**data)
        self.assertEqual(schema.name, "Spring Championship")
        self.assertIsNone(schema.venue_public_id)
        self.assertEqual(schema.coach_public_ids, [])
        self.assertEqual(schema.athlete_public_ids, [])
        self.assertIsNone(schema.score)

    def test_missing_required_name(self):
        """Test that missing name raises validation error."""
        data = {
            "date": "2025-04-15T10:00:00Z",
            "season_public_id": "season123",
        }
        with self.assertRaises(ValidationError) as context:
            CompetitionIn(**data)
        self.assertIn("name", str(context.exception))

    def test_missing_required_date(self):
        """Test that missing date raises validation error."""
        data = {
            "name": "Spring Championship",
            "season_public_id": "season123",
        }
        with self.assertRaises(ValidationError) as context:
            CompetitionIn(**data)
        self.assertIn("date", str(context.exception))

    def test_missing_required_season(self):
        """Test that missing season_public_id raises validation error."""
        data = {
            "name": "Spring Championship",
            "date": "2025-04-15T10:00:00Z",
        }
        with self.assertRaises(ValidationError) as context:
            CompetitionIn(**data)
        self.assertIn("season_public_id", str(context.exception))


class CompetitionPatchSchemaTest(TestCase):
    """Test CompetitionPatch schema for partial updates."""

    def test_all_fields_optional(self):
        """Test that all fields are optional for PATCH."""
        schema = CompetitionPatch()
        self.assertIsNone(schema.name)
        self.assertIsNone(schema.date)
        self.assertIsNone(schema.score)

    def test_exclude_unset_returns_only_provided_fields(self):
        """Test model_dump(exclude_unset=True) returns only provided fields."""
        schema = CompetitionPatch(name="Updated Competition")
        data = schema.model_dump(exclude_unset=True)
        self.assertEqual(data, {"name": "Updated Competition"})
