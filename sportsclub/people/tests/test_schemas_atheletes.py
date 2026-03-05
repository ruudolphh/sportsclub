# people/tests/test_schemas_athletes.py

from django.test import TestCase
from pydantic import ValidationError

from people.schemas import (
    AthleteIn,
    AthletePatch,
    AthleteRef,
    PersonRef,
)


class AthleteInSchemaTest(TestCase):
    """Test AthleteIn schema validation."""

    def test_valid_full_athlete(self):
        """Test validation with all fields."""
        data = {
            "first_name": "Usain",
            "last_name": "Bolt",
            "email": "usain.bolt@example.com",
            "phone": "+1234567890",
            "date_of_birth": "1986-08-21",
            "address_public_id": "abc123",
            "height": 195.0,
            "weight": 94.0,
            "jersey_number": 9,
        }
        schema = AthleteIn(**data)
        self.assertEqual(schema.first_name, "Usain")
        self.assertEqual(schema.last_name, "Bolt")
        self.assertEqual(schema.email, "usain.bolt@example.com")
        self.assertEqual(schema.height, 195.0)

    def test_valid_minimal_athlete(self):
        """Test validation with only required fields."""
        data = {
            "first_name": "Usain",
            "last_name": "Bolt",
            "email": "usain@example.com",
        }
        schema = AthleteIn(**data)
        self.assertEqual(schema.first_name, "Usain")
        self.assertEqual(schema.phone, "")
        self.assertIsNone(schema.height)
        self.assertIsNone(schema.jersey_number)

    def test_missing_required_first_name(self):
        """Test that missing first_name raises validation error."""
        data = {"last_name": "Bolt", "email": "usain@example.com"}
        with self.assertRaises(ValidationError) as context:
            AthleteIn(**data)
        self.assertIn("first_name", str(context.exception))

    def test_missing_required_last_name(self):
        """Test that missing last_name raises validation error."""
        data = {"first_name": "Usain", "email": "usain@example.com"}
        with self.assertRaises(ValidationError) as context:
            AthleteIn(**data)
        self.assertIn("last_name", str(context.exception))

    def test_missing_required_email(self):
        """Test that missing email raises validation error."""
        data = {"first_name": "Usain", "last_name": "Bolt"}
        with self.assertRaises(ValidationError) as context:
            AthleteIn(**data)
        self.assertIn("email", str(context.exception))

    def test_invalid_email_format(self):
        """Test that invalid email format raises validation error."""
        data = {
            "first_name": "Usain",
            "last_name": "Bolt",
            "email": "not-an-email",
        }
        with self.assertRaises(ValidationError) as context:
            AthleteIn(**data)
        self.assertIn("email", str(context.exception))

    def test_first_name_too_long(self):
        """Test that first_name exceeding max_length raises error."""
        data = {
            "first_name": "U" * 101,
            "last_name": "Bolt",
            "email": "usain@example.com",
        }
        with self.assertRaises(ValidationError) as context:
            AthleteIn(**data)
        self.assertIn("first_name", str(context.exception))

    def test_height_must_be_positive(self):
        """Test that height must be greater than zero."""
        data = {
            "first_name": "Usain",
            "last_name": "Bolt",
            "email": "usain@example.com",
            "height": 0,
        }
        with self.assertRaises(ValidationError) as context:
            AthleteIn(**data)
        self.assertIn("height", str(context.exception))

    def test_weight_must_be_positive(self):
        """Test that weight must be greater than zero."""
        data = {
            "first_name": "Usain",
            "last_name": "Bolt",
            "email": "usain@example.com",
            "weight": -5.0,
        }
        with self.assertRaises(ValidationError) as context:
            AthleteIn(**data)
        self.assertIn("weight", str(context.exception))


class AthletePatchSchemaTest(TestCase):
    """Test AthletePatch schema for partial updates."""

    def test_all_fields_optional(self):
        """Test that all fields are optional for PATCH."""
        schema = AthletePatch()
        self.assertIsNone(schema.first_name)
        self.assertIsNone(schema.last_name)
        self.assertIsNone(schema.email)

    def test_exclude_unset_returns_only_provided_fields(self):
        """Test model_dump(exclude_unset=True) returns only provided fields."""
        schema = AthletePatch(first_name="Updated", height=180.0)
        data = schema.model_dump(exclude_unset=True)
        self.assertEqual(data, {"first_name": "Updated", "height": 180.0})

    def test_partial_update_with_email(self):
        """Test partial update with valid email."""
        schema = AthletePatch(email="new.email@example.com")
        data = schema.model_dump(exclude_unset=True)
        self.assertEqual(data, {"email": "new.email@example.com"})

    def test_invalid_email_in_patch(self):
        """Test that invalid email raises error even in PATCH."""
        with self.assertRaises(ValidationError):
            AthletePatch(email="invalid-email")


class AthleteRefSchemaTest(TestCase):
    """Test AthleteRef schema."""

    def test_athlete_ref_inherits_from_person_ref(self):
        """Test that AthleteRef inherits from PersonRef."""
        self.assertTrue(issubclass(AthleteRef, PersonRef))

    def test_athlete_ref_has_jersey_number(self):
        """Test that AthleteRef includes jersey_number field."""
        schema = AthleteRef(
            public_id="abc123", display_name="Usain Bolt", jersey_number=9
        )
        self.assertEqual(schema.jersey_number, 9)
