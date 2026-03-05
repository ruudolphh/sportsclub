# core/tests/test_models_address.py
"""Unit tests for the Address model."""

from django.test import TestCase
from inventory.models import Venue

from core.models import Address


class AddressCreationTest(TestCase):
    """Tests for creating Address instances."""

    def test_create_minimal_address(self):
        """Test creating an address with only required fields."""
        address = Address.objects.create(line1="Plaça de la Navegació, s/n")

        self.assertIsNotNone(address.id)
        self.assertIsNotNone(address.public_id)
        self.assertEqual(address.line1, "Plaça de la Navegació, s/n")
        self.assertEqual(address.line2, "")
        self.assertEqual(address.city, "")

    def test_create_full_address(self):
        """Test creating an address with all fields."""
        address = Address.objects.create(
            line1="Av. de Jaume III, 15",
            line2="Centre",
            postal_code="07012",
            city="Palma",
            state="Illes Balears",
            country="Spain",
        )

        self.assertEqual(address.line1, "Av. de Jaume III, 15")
        self.assertEqual(address.line2, "Centre")
        self.assertEqual(address.postal_code, "07012")
        self.assertEqual(address.city, "Palma")
        self.assertEqual(address.state, "Illes Balears")
        self.assertEqual(address.country, "Spain")


class AddressPublicIDTest(TestCase):
    """Tests for Address public_id field behavior."""

    def test_public_id_is_automatically_generated(self):
        """Test that public_id is automatically generated on creation."""
        address = Address.objects.create(line1="Test Address")

        self.assertIsNotNone(address.public_id)
        self.assertGreater(len(address.public_id), 0)

    def test_public_id_is_unique(self):
        """Test that each address gets a unique public_id."""
        address1 = Address.objects.create(line1="First Address")
        address2 = Address.objects.create(line1="Second Address")

        self.assertIsNotNone(address1.public_id)
        self.assertIsNotNone(address2.public_id)
        self.assertNotEqual(address1.public_id, address2.public_id)

    def test_public_id_is_not_editable_in_forms(self):
        """Test that public_id field is marked as non-editable."""
        field = Address._meta.get_field("public_id")
        self.assertFalse(field.editable)


class AddressStringRepresentationTest(TestCase):
    """Tests for Address.__str__() method."""

    def test_str_representation_full(self):
        """Test __str__ with all fields populated."""
        address = Address.objects.create(
            line1="Av. de Jaume III, 15",
            line2="Centre",
            postal_code="07012",
            city="Palma",
            state="Illes Balears",
            country="Spain",
        )
        expected = "Av. de Jaume III, 15, Centre, 07012 Palma, Illes Balears, Spain"
        self.assertEqual(str(address), expected)

    def test_str_representation_without_line2(self):
        """Test __str__ without secondary address line."""
        address = Address.objects.create(
            line1="Carrer de Pelaires, 30",
            postal_code="07012",
            city="Palma",
            state="Illes Balears",
            country="Spain",
        )
        expected = "Carrer de Pelaires, 30, 07012 Palma, Illes Balears, Spain"
        self.assertEqual(str(address), expected)

    def test_str_representation_minimal(self):
        """Test __str__ with only line1 (minimum required field)."""
        address = Address.objects.create(line1="Plaça de la Navegació, s/n")
        self.assertEqual(str(address), "Plaça de la Navegació, s/n")

    def test_str_representation_no_postal_code(self):
        """Test __str__ without postal code."""
        address = Address.objects.create(
            line1="Plaça de la Navegació, s/n", city="Palma", country="Spain"
        )
        expected = "Plaça de la Navegació, s/n, Palma, Spain"
        self.assertEqual(str(address), expected)

    def test_str_representation_only_line1_and_country(self):
        """Test __str__ with only line1 and country."""
        address = Address.objects.create(line1="Main Street", country="Spain")
        expected = "Main Street, Spain"
        self.assertEqual(str(address), expected)

    def test_str_representation_with_state_no_city(self):
        """Test __str__ with state but no city (edge case)."""
        address = Address.objects.create(
            line1="Rural Road", state="Illes Balears", country="Spain"
        )
        expected = "Rural Road, Illes Balears, Spain"
        self.assertEqual(str(address), expected)


class AddressMetaConfigurationTest(TestCase):
    """Tests for Address model Meta configuration."""

    def test_verbose_name(self):
        """Test that verbose_name is correctly set."""
        self.assertEqual(Address._meta.verbose_name, "Address")

    def test_verbose_name_plural(self):
        """Test that verbose_name_plural is correctly set."""
        self.assertEqual(Address._meta.verbose_name_plural, "Addresses")

    def test_database_indexes_exist(self):
        """Test that database indexes are properly configured."""
        indexes = Address._meta.indexes

        self.assertEqual(len(indexes), 1)
        self.assertEqual(indexes[0].fields, ["city", "country"])

    def test_composite_index_field_order(self):
        """Test that composite index has correct field order for query optimization."""
        # The index should be (city, country) to support queries like:
        # - WHERE city = 'Palma' AND country = 'Spain'
        # - WHERE city = 'Palma' (uses leftmost prefix)
        indexes = Address._meta.indexes
        index_fields = indexes[0].fields

        self.assertEqual(index_fields[0], "city")
        self.assertEqual(index_fields[1], "country")


class AddressQueryMethodsTest(TestCase):
    """Tests for Address model query methods."""

    def test_get_orphaned_addresses_returns_orphaned(self):
        """Test that get_orphaned_addresses() returns addresses with no relations."""
        address1 = Address.objects.create(line1="First Address", city="Palma")
        address2 = Address.objects.create(line1="Second Address", city="Barcelona")

        orphaned = Address.get_orphaned_addresses()

        self.assertEqual(orphaned.count(), 2)
        self.assertIn(address1, orphaned)
        self.assertIn(address2, orphaned)

    def test_get_orphaned_addresses_excludes_linked(self):
        """Test that addresses with relations are not orphaned."""
        address1 = Address.objects.create(line1="First Address", city="Palma")
        address2 = Address.objects.create(line1="Second Address", city="Barcelona")

        # Fixture
        Venue.objects.create(name="Stadium", address=address1)

        orphaned = Address.get_orphaned_addresses()

        self.assertEqual(orphaned.count(), 1)
        self.assertIn(address2, orphaned)
        self.assertNotIn(address1, orphaned)
