# inventory/tests/test_schemas.py
"""Unit tests for Venue schemas (validation, serialization)."""

from core.models import Address
from django.test import TestCase
from pydantic import ValidationError

from inventory.models import Venue, VenueType
from inventory.schemas import (
    VenueIn,
    VenueListOut,
    VenueOut,
    VenuePatch,
    VenueRef,
)


class VenueInSchemaTest(TestCase):
    """Test the VenueIn schema validation."""

    def test_valid_full_venue(self):
        """Test validation with all fields."""
        data = {
            "name": "Camp Nou",
            "venue_type": VenueType.STADIUM,
            "capacity": 99354,
            "address_public_id": "abc123",
            "indoor": False,
        }
        schema = VenueIn(**data)

        self.assertEqual(schema.name, "Camp Nou")
        self.assertEqual(schema.venue_type, VenueType.STADIUM)
        self.assertEqual(schema.capacity, 99354)
        self.assertEqual(schema.address_public_id, "abc123")
        self.assertFalse(schema.indoor)

    def test_valid_minimal_venue(self):
        """Test validation with only required field."""
        data = {"name": "Local Track"}
        schema = VenueIn(**data)

        self.assertEqual(schema.name, "Local Track")
        self.assertEqual(schema.venue_type, VenueType.FIELD)  # Default
        self.assertIsNone(schema.capacity)
        self.assertIsNone(schema.address_public_id)
        self.assertFalse(schema.indoor)

    def test_missing_required_name(self):
        """Test that missing name raises validation error."""
        data = {"venue_type": VenueType.STADIUM}

        with self.assertRaises(ValidationError) as context:
            VenueIn(**data)

        errors = context.exception.errors()
        self.assertTrue(any(e["loc"] == ("name",) for e in errors))

    def test_empty_name_fails(self):
        """Test that empty name fails validation (min_length=1)."""
        data = {"name": ""}

        with self.assertRaises(ValidationError) as context:
            VenueIn(**data)

        errors = context.exception.errors()
        self.assertTrue(any(e["loc"] == ("name",) for e in errors))

    def test_name_too_long(self):
        """Test that name exceeding max_length fails."""
        data = {"name": "x" * 201}

        with self.assertRaises(ValidationError) as context:
            VenueIn(**data)

        errors = context.exception.errors()
        self.assertTrue(
            any(
                e["loc"] == ("name",) and e["type"] == "string_too_long" for e in errors
            )
        )

    def test_negative_capacity_fails(self):
        """Test that negative capacity fails validation."""
        data = {"name": "Test Venue", "capacity": -100}

        with self.assertRaises(ValidationError) as context:
            VenueIn(**data)

        errors = context.exception.errors()
        self.assertTrue(any(e["loc"] == ("capacity",) for e in errors))

    def test_zero_capacity_allowed(self):
        """Test that zero capacity is allowed."""
        data = {"name": "Test Venue", "capacity": 0}
        schema = VenueIn(**data)

        self.assertEqual(schema.capacity, 0)

    def test_invalid_venue_type_fails(self):
        """Test that invalid venue_type fails validation."""
        data = {"name": "Test Venue", "venue_type": "invalid_type"}

        with self.assertRaises(ValidationError):
            VenueIn(**data)

    def test_all_venue_types_valid(self):
        """Test that all VenueType values are accepted."""
        for venue_type in VenueType:
            with self.subTest(venue_type=venue_type):
                data = {"name": "Test Venue", "venue_type": venue_type}
                schema = VenueIn(**data)
                self.assertEqual(schema.venue_type, venue_type)


class VenuePatchSchemaTest(TestCase):
    """Test the VenuePatch schema validation for partial updates."""

    def test_all_fields_optional(self):
        """Test that all fields are optional for PATCH."""
        data = {}
        schema = VenuePatch(**data)

        self.assertIsNone(schema.name)
        self.assertIsNone(schema.venue_type)
        self.assertIsNone(schema.capacity)
        self.assertIsNone(schema.address_public_id)
        self.assertIsNone(schema.indoor)

    def test_single_field_update(self):
        """Test updating a single field."""
        data = {"name": "Updated Name"}
        schema = VenuePatch(**data)

        self.assertEqual(schema.name, "Updated Name")
        self.assertIsNone(schema.venue_type)

    def test_multiple_fields_update(self):
        """Test updating multiple fields."""
        data = {"name": "New Stadium", "capacity": 50000, "indoor": True}
        schema = VenuePatch(**data)

        self.assertEqual(schema.name, "New Stadium")
        self.assertEqual(schema.capacity, 50000)
        self.assertTrue(schema.indoor)

    def test_name_min_length_when_provided(self):
        """Test that name still respects min_length when provided."""
        data = {"name": ""}

        with self.assertRaises(ValidationError) as context:
            VenuePatch(**data)

        errors = context.exception.errors()
        self.assertTrue(any(e["loc"] == ("name",) for e in errors))

    def test_exclude_unset_returns_only_provided_fields(self):
        """Test that model_dump(exclude_unset=True) returns only provided fields."""
        data = {"name": "Updated Name", "indoor": True}
        schema = VenuePatch(**data)

        dumped = schema.model_dump(exclude_unset=True)

        self.assertEqual(dumped, {"name": "Updated Name", "indoor": True})
        self.assertNotIn("venue_type", dumped)
        self.assertNotIn("capacity", dumped)


class VenueOutSchemaTest(TestCase):
    """Test the VenueOut schema serialization."""

    def test_serialize_venue_with_address(self):
        """Test serializing a Venue model with address to VenueOut schema."""
        address = Address.objects.create(
            line1="Carrer de les Corts, 1",
            city="Barcelona",
            country="Spain",
        )
        venue = Venue.objects.create(
            name="Camp Nou",
            venue_type=VenueType.STADIUM,
            capacity=99354,
            address=address,
            indoor=False,
        )

        schema = VenueOut.model_validate(venue)

        self.assertEqual(schema.public_id, venue.public_id)
        self.assertEqual(schema.name, "Camp Nou")
        self.assertEqual(schema.venue_type, VenueType.STADIUM)
        self.assertEqual(schema.capacity, 99354)
        self.assertFalse(schema.indoor)
        self.assertIsNotNone(schema.address)
        self.assertEqual(schema.address.city, "Barcelona")

    def test_serialize_venue_without_address(self):
        """Test serializing a Venue model without address."""
        venue = Venue.objects.create(
            name="Local Field",
            venue_type=VenueType.FIELD,
        )

        schema = VenueOut.model_validate(venue)

        self.assertEqual(schema.name, "Local Field")
        self.assertIsNone(schema.address)

    def test_serialize_venue_with_null_capacity(self):
        """Test serializing venue with null capacity."""
        venue = Venue.objects.create(name="Open Field")

        schema = VenueOut.model_validate(venue)

        self.assertIsNone(schema.capacity)


class VenueListOutSchemaTest(TestCase):
    """Test the VenueListOut schema for list views."""

    def test_serialize_for_list_view(self):
        """Test serializing venue for list view (minimal fields)."""
        venue = Venue.objects.create(
            name="Camp Nou",
            venue_type=VenueType.STADIUM,
            capacity=99354,
            indoor=False,
        )

        schema = VenueListOut.model_validate(venue)

        self.assertEqual(schema.public_id, venue.public_id)
        self.assertEqual(schema.name, "Camp Nou")
        self.assertEqual(schema.venue_type, VenueType.STADIUM)
        self.assertFalse(schema.indoor)

        # These fields should NOT be in VenueListOut
        self.assertFalse(hasattr(schema, "capacity"))
        self.assertFalse(hasattr(schema, "address"))

    def test_list_out_is_lightweight(self):
        """Test that VenueListOut has fewer fields than VenueOut."""
        venue = Venue.objects.create(
            name="Test Venue",
            venue_type=VenueType.GYMNASIUM,
        )

        list_schema = VenueListOut.model_validate(venue)
        full_schema = VenueOut.model_validate(venue)

        list_dict = list_schema.model_dump()
        full_dict = full_schema.model_dump()

        self.assertLess(len(list_dict), len(full_dict))


class VenueRefSchemaTest(TestCase):
    """Test the VenueRef schema for embedding in related resources."""

    def test_serialize_venue_ref(self):
        """Test serializing a venue reference."""
        venue = Venue.objects.create(
            name="Municipal Stadium",
            venue_type=VenueType.STADIUM,
            capacity=25000,
        )

        schema = VenueRef.model_validate(venue)

        self.assertEqual(schema.public_id, venue.public_id)
        self.assertEqual(schema.name, "Municipal Stadium")

        # Should only have these two fields
        dumped = schema.model_dump()
        self.assertEqual(set(dumped.keys()), {"public_id", "name"})
