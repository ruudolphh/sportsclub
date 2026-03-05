# people/tests/test_models_athlete.py
from datetime import date

from core.models import Address
from django.db import IntegrityError
from django.test import TestCase

from people.models import Athlete


class AthleteModelTest(TestCase):
    """Test suite for Athlete model."""

    def setUp(self):
        """Set up test data."""
        self.address = Address.objects.create(
            line1="123 Track Lane",
            city="Barcelona",
            postal_code="08001",
            country="ES",
        )
        self.athlete = Athlete.objects.create(
            first_name="Usain",
            last_name="Bolt",
            email="usain.bolt@example.com",
            phone="+1234567890",
            date_of_birth=date(1986, 8, 21),
            address=self.address,
            height=195.0,
            weight=94.0,
            jersey_number=9,
        )

    def test_create_athlete_minimal(self):
        """Test creating athlete with only required fields."""
        athlete = Athlete.objects.create(
            first_name="Carl",
            last_name="Lewis",
            email="carl.lewis@example.com",
        )
        self.assertIsNotNone(athlete.pk)
        self.assertIsNotNone(athlete.public_id)
        self.assertEqual(athlete.phone, "")
        self.assertIsNone(athlete.height)

    def test_str_representation(self):
        """Test __str__ returns full name."""
        self.assertEqual(str(self.athlete), "Usain Bolt")

    def test_public_id_generated_automatically(self):
        """Test that public_id is auto-generated."""
        self.assertIsNotNone(self.athlete.public_id)
        self.assertGreater(len(self.athlete.public_id), 0)

    def test_public_id_is_unique(self):
        """Test that each athlete gets a unique public_id."""
        athlete2 = Athlete.objects.create(
            first_name="Carl",
            last_name="Lewis",
            email="carl.lewis@example.com",
        )
        self.assertNotEqual(self.athlete.public_id, athlete2.public_id)

    def test_email_must_be_unique(self):
        """Test that duplicate emails raise IntegrityError."""
        with self.assertRaises(IntegrityError):
            Athlete.objects.create(
                first_name="Fake",
                last_name="Bolt",
                email="usain.bolt@example.com",
            )

    def test_address_relationship(self):
        """Test athlete can have an address."""
        self.assertEqual(self.athlete.address, self.address)
        self.assertEqual(self.athlete.address.city, "Barcelona")

    def test_address_nullable(self):
        """Test athlete can exist without address."""
        athlete = Athlete.objects.create(
            first_name="Carl",
            last_name="Lewis",
            email="carl.lewis@example.com",
        )
        self.assertIsNone(athlete.address)

    def test_address_set_null_on_delete(self):
        """Test that deleting address sets athlete.address to null."""
        self.address.delete()
        self.athlete.refresh_from_db()
