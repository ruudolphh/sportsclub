# people/tests/test_schemas_coaches.py
from django.test import TestCase
from pydantic import ValidationError

from people.models import CoachingCertification
from people.schemas import (
    CoachIn,
    CoachPatch,
    CoachRef,
    PersonRef,
)


class CoachInSchemaTest(TestCase):
    """Test CoachIn schema validation."""

    def test_valid_full_coach(self):
        """Test validation with all fields."""
        data = {
            "first_name": "Carlo",
            "last_name": "Ancelotti",
            "email": "carlo.ancelotti@example.com",
            "phone": "+1234567890",
            "date_of_birth": "1959-06-10",
            "address_public_id": "abc123",
            "certification": CoachingCertification.ENTRENADOR_NACIONAL,
        }
        schema = CoachIn(**data)
        self.assertEqual(schema.first_name, "Carlo")
        self.assertEqual(
            schema.certification, CoachingCertification.ENTRENADOR_NACIONAL
        )

    def test_valid_minimal_coach(self):
        """Test validation with only required fields."""
        data = {
            "first_name": "Carlo",
            "last_name": "Ancelotti",
            "email": "carlo@example.com",
        }
        schema = CoachIn(**data)
        self.assertEqual(schema.first_name, "Carlo")
        self.assertIsNone(schema.certification)

    def test_invalid_certification(self):
        """Test that invalid certification raises validation error."""
        data = {
            "first_name": "Carlo",
            "last_name": "Ancelotti",
            "email": "carlo@example.com",
            "certification": "INVALID",
        }
        with self.assertRaises(ValidationError) as context:
            CoachIn(**data)
        self.assertIn("certification", str(context.exception))


class CoachPatchSchemaTest(TestCase):
    """Test CoachPatch schema for partial updates."""

    def test_all_fields_optional(self):
        """Test that all fields are optional for PATCH."""
        schema = CoachPatch()
        self.assertIsNone(schema.first_name)
        self.assertIsNone(schema.certification)

    def test_exclude_unset_returns_only_provided_fields(self):
        """Test model_dump(exclude_unset=True) returns only provided fields."""
        schema = CoachPatch(certification=CoachingCertification.ENTRENADOR_CLUB)
        data = schema.model_dump(exclude_unset=True)
        self.assertEqual(data, {"certification": CoachingCertification.ENTRENADOR_CLUB})


class CoachRefSchemaTest(TestCase):
    """Test CoachRef schema."""

    def test_coach_ref_inherits_from_person_ref(self):
        """Test that CoachRef inherits from PersonRef."""
        self.assertTrue(issubclass(CoachRef, PersonRef))
