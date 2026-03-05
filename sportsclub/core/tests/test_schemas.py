# core/tests/test_schemas.py
"""Unit tests for Ninja schemas (validation, serialization)."""

from django.test import TestCase
from pydantic import ValidationError

from core.models.address import Address
from core.schemas import AddressIn, AddressListOut, AddressOut, AddressPatch


class AddressInSchemaTest(TestCase):
    """Test the AddressIn schema validation."""

    def test_valid_full_address(self):
        """Test validation with all fields."""
        data = {
            "line1": "Av. de Jaume III, 15",
            "line2": "Centre",
            "postal_code": "07012",
            "city": "Palma",
            "state": "Illes Balears",
            "country": "Spain",
        }
        schema = AddressIn(**data)

        self.assertEqual(schema.line1, "Av. de Jaume III, 15")
        self.assertEqual(schema.line2, "Centre")
        self.assertEqual(schema.postal_code, "07012")
        self.assertEqual(schema.city, "Palma")
        self.assertEqual(schema.state, "Illes Balears")
        self.assertEqual(schema.country, "Spain")

    def test_valid_minimal_address(self):
        """Test validation with only required field."""
        data = {"line1": "Carrer de Pelaires, 30"}
        schema = AddressIn(**data)

        self.assertEqual(schema.line1, "Carrer de Pelaires, 30")
        self.assertEqual(schema.line2, "")
        self.assertEqual(schema.postal_code, "")
        self.assertEqual(schema.city, "")
        self.assertEqual(schema.state, "")
        self.assertEqual(schema.country, "")

    def test_missing_required_line1(self):
        """Test that missing line1 raises validation error."""
        data = {"city": "Palma"}

        with self.assertRaises(ValidationError) as context:
            AddressIn(**data)

        errors = context.exception.errors()
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0]["loc"], ("line1",))
        self.assertEqual(errors[0]["type"], "missing")

    def test_empty_line1_fails(self):
        """Test that empty line1 fails validation (min_length=1)."""
        data = {"line1": ""}

        with self.assertRaises(ValidationError) as context:
            AddressIn(**data)

        errors = context.exception.errors()
        self.assertTrue(any(e["loc"] == ("line1",) for e in errors))

    def test_line1_too_long(self):
        """Test that line1 exceeding max_length fails."""
        data = {"line1": "x" * 256}  # Max is 255

        with self.assertRaises(ValidationError) as context:
            AddressIn(**data)

        errors = context.exception.errors()
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0]["loc"], ("line1",))
        self.assertEqual(errors[0]["type"], "string_too_long")

    def test_line1_at_max_length(self):
        """Test that line1 at exactly max_length is valid."""
        data = {"line1": "x" * 255}
        schema = AddressIn(**data)

        self.assertEqual(len(schema.line1), 255)

    def test_postal_code_whitespace_is_stripped(self):
        """Test that postal code validator strips whitespace."""
        data = {"line1": "Test Street", "postal_code": "  07012  "}

        schema = AddressIn(**data)

        self.assertEqual(schema.postal_code, "07012")

    def test_postal_code_empty_string_allowed(self):
        """Test that empty postal code is allowed."""
        data = {"line1": "Test Street", "postal_code": ""}

        schema = AddressIn(**data)

        self.assertEqual(schema.postal_code, "")

    def test_optional_fields_default_to_empty_string(self):
        """Test that optional fields default to empty string."""
        data = {"line1": "Main Street"}
        schema = AddressIn(**data)

        self.assertEqual(schema.line2, "")
        self.assertEqual(schema.postal_code, "")
        self.assertEqual(schema.city, "")
        self.assertEqual(schema.state, "")
        self.assertEqual(schema.country, "")

    def test_line2_max_length(self):
        """Test that line2 respects max_length."""
        data = {"line1": "Test", "line2": "x" * 256}

        with self.assertRaises(ValidationError):
            AddressIn(**data)

    def test_all_fields_max_length_validation(self):
        """Test that all fields respect their max_length constraints."""
        test_cases = [
            ("line1", 256),  # Max is 255
            ("line2", 256),  # Max is 255
            ("postal_code", 21),  # Max is 20
            ("city", 101),  # Max is 100
            ("state", 101),  # Max is 100
            ("country", 101),  # Max is 100
        ]

        for field_name, length in test_cases:
            with self.subTest(field=field_name):
                data = {"line1": "Test Street", field_name: "x" * length}

                with self.assertRaises(ValidationError) as context:
                    AddressIn(**data)

                errors = context.exception.errors()
                self.assertTrue(
                    any(e["loc"] == (field_name,) for e in errors),
                    f"Expected validation error for {field_name}",
                )


class AddressOutSchemaTest(TestCase):
    """Test the AddressOut schema serialization."""

    def test_serialize_address(self):
        """Test serializing an Address model to AddressOut schema."""
        address = Address.objects.create(
            line1="Av. de Jaume III, 15",
            line2="Centre",
            postal_code="07012",
            city="Palma",
            state="Illes Balears",
            country="Spain",
        )

        schema = AddressOut.model_validate(address)

        self.assertEqual(schema.public_id, address.public_id)
        self.assertEqual(schema.line1, "Av. de Jaume III, 15")
        self.assertEqual(schema.line2, "Centre")
        self.assertEqual(schema.postal_code, "07012")
        self.assertEqual(schema.city, "Palma")
        self.assertEqual(schema.state, "Illes Balears")
        self.assertEqual(schema.country, "Spain")

    def test_serialize_minimal_address(self):
        """Test serializing address with minimal fields."""
        address = Address.objects.create(line1="Simple Street")

        schema = AddressOut.model_validate(address)

        self.assertEqual(schema.line1, "Simple Street")
        self.assertEqual(schema.line2, "")
        self.assertEqual(schema.city, "")

    def test_formatted_address_computed_field(self):
        """Test that formatted_address is computed from __str__ method."""
        address = Address.objects.create(
            line1="Av. de Jaume III, 15",
            city="Palma",
            state="Illes Balears",
            country="Spain",
        )

        schema = AddressOut.model_validate(address)

        expected_formatted = str(address)
        self.assertEqual(schema.formatted_address, expected_formatted)
        self.assertIn("Av. de Jaume III, 15", schema.formatted_address)
        self.assertIn("Palma", schema.formatted_address)


class AddressListOutSchemaTest(TestCase):
    """Test the AddressListOut schema for list views."""

    def test_serialize_for_list_view(self):
        """Test serializing address for list view (minimal fields)."""
        address = Address.objects.create(
            line1="Av. de Jaume III, 15",
            line2="Centre",
            postal_code="07012",
            city="Palma",
            state="Illes Balears",
            country="Spain",
        )

        schema = AddressListOut.model_validate(address)

        # Check only list view fields are present
        self.assertEqual(schema.public_id, address.public_id)
        self.assertIsNotNone(schema.formatted_address)

        # These fields should NOT be in AddressListOut
        self.assertFalse(hasattr(schema, "line1"))
        self.assertFalse(hasattr(schema, "line2"))
        self.assertFalse(hasattr(schema, "postal_code"))
        self.assertFalse(hasattr(schema, "city"))
        self.assertFalse(hasattr(schema, "state"))
        self.assertFalse(hasattr(schema, "country"))

    def test_formatted_address_uses_str_method(self):
        """Test that formatted_address uses the model's __str__ method."""
        address = Address.objects.create(
            line1="Carrer de Pelaires, 30",
            postal_code="07012",
            city="Palma",
            country="Spain",
        )

        schema = AddressListOut.model_validate(address)

        expected = str(address)
        self.assertEqual(schema.formatted_address, expected)

    def test_list_out_is_lightweight(self):
        """Test that AddressListOut has fewer fields than AddressOut."""
        address = Address.objects.create(
            line1="Test",
            city="Palma",
            country="Spain",
        )

        list_schema = AddressListOut.model_validate(address)
        full_schema = AddressOut.model_validate(address)

        # Convert to dict to count fields
        list_dict = list_schema.model_dump()
        full_dict = full_schema.model_dump()

        self.assertLess(len(list_dict), len(full_dict))
        self.assertEqual(len(list_dict), 2)  # public_id + formatted_address


class SchemaIntegrationTest(TestCase):
    """Integration tests for schemas working with models."""

    def test_round_trip_create_and_serialize(self):
        """Test creating from AddressIn and serializing to AddressOut."""
        # Step 1: Validate input
        input_data = {
            "line1": "Av. de Jaume III, 15",
            "line2": "Centre",
            "postal_code": "07012",
            "city": "Palma",
            "state": "Illes Balears",
            "country": "Spain",
        }
        address_in = AddressIn(**input_data)

        # Step 2: Create model from validated input
        address = Address.objects.create(**address_in.model_dump())

        # Step 3: Serialize to output schema
        address_out = AddressOut.model_validate(address)

        # Verify data integrity
        self.assertEqual(address_out.line1, input_data["line1"])
        self.assertEqual(address_out.city, input_data["city"])
        self.assertIsNotNone(address_out.public_id)

    def test_postal_code_whitespace_stripping_end_to_end(self):
        """Test that postal code whitespace is stripped throughout the flow."""
        input_data = {"line1": "Test Street", "postal_code": "  07012  "}

        # Validate input (should strip whitespace)
        address_in = AddressIn(**input_data)
        self.assertEqual(address_in.postal_code, "07012")

        # Create model
        address = Address.objects.create(**address_in.model_dump())

        # Serialize output
        address_out = AddressOut.model_validate(address)
        self.assertEqual(address_out.postal_code, "07012")


# Add this class to core/tests/test_schemas.py


class AddressPatchSchemaTest(TestCase):
    """Test the AddressPatch schema validation for partial updates."""

    def test_all_fields_optional(self):
        """Test that all fields are optional for PATCH."""
        data = {}
        schema = AddressPatch(**data)

        self.assertIsNone(schema.line1)
        self.assertIsNone(schema.line2)
        self.assertIsNone(schema.postal_code)
        self.assertIsNone(schema.city)
        self.assertIsNone(schema.state)
        self.assertIsNone(schema.country)

    def test_single_field_update(self):
        """Test updating a single field."""
        data = {"city": "Barcelona"}
        schema = AddressPatch(**data)

        self.assertIsNone(schema.line1)
        self.assertEqual(schema.city, "Barcelona")

    def test_multiple_fields_update(self):
        """Test updating multiple fields."""
        data = {"city": "Barcelona", "postal_code": "08001"}
        schema = AddressPatch(**data)

        self.assertEqual(schema.city, "Barcelona")
        self.assertEqual(schema.postal_code, "08001")
        self.assertIsNone(schema.line1)

    def test_line1_min_length_when_provided(self):
        """Test that line1 still respects min_length when provided."""
        data = {"line1": ""}

        with self.assertRaises(ValidationError) as context:
            AddressPatch(**data)

        errors = context.exception.errors()
        self.assertTrue(any(e["loc"] == ("line1",) for e in errors))

    def test_line1_max_length_when_provided(self):
        """Test that line1 still respects max_length when provided."""
        data = {"line1": "x" * 256}

        with self.assertRaises(ValidationError) as context:
            AddressPatch(**data)

        errors = context.exception.errors()
        self.assertTrue(any(e["loc"] == ("line1",) for e in errors))

    def test_exclude_unset_returns_only_provided_fields(self):
        """Test that model_dump(exclude_unset=True) returns only provided fields."""
        data = {"city": "Sevilla", "country": "Spain"}
        schema = AddressPatch(**data)

        dumped = schema.model_dump(exclude_unset=True)

        self.assertEqual(dumped, {"city": "Sevilla", "country": "Spain"})
        self.assertNotIn("line1", dumped)
        self.assertNotIn("line2", dumped)

    def test_all_fields_max_length_validation(self):
        """Test that all fields respect their max_length when provided."""
        test_cases = [
            ("line1", 256),
            ("line2", 256),
            ("postal_code", 21),
            ("city", 101),
            ("state", 101),
            ("country", 101),
        ]

        for field_name, length in test_cases:
            with self.subTest(field=field_name):
                data = {field_name: "x" * length}

                with self.assertRaises(ValidationError) as context:
                    AddressPatch(**data)

                errors = context.exception.errors()
                self.assertTrue(
                    any(e["loc"] == (field_name,) for e in errors),
                    f"Expected validation error for {field_name}",
                )
