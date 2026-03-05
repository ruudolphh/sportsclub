# people/tests/test_models_coach.py
from datetime import date

from core.models import Address
from django.db import IntegrityError
from django.test import TestCase

from people.models import Coach, CoachingCertification


class CoachModelTest(TestCase):
    """Test suite for Coach model."""

    def setUp(self):
        """Set up test data."""
        self.address = Address.objects.create(
            line1="456 Stadium Road",
            city="Madrid",
            postal_code="28001",
            country="ES",
        )
        self.coach = Coach.objects.create(
            first_name="Carlo",
            last_name="Ancelotti",
            email="carlo.ancelotti@example.com",
            phone="+1234567890",
            date_of_birth=date(1959, 6, 10),
            address=self.address,
            certification=CoachingCertification.ENTRENADOR_NACIONAL,
        )

    def test_create_coach_minimal(self):
        """Test creating coach with only required fields."""
        coach = Coach.objects.create(
            first_name="Pep",
            last_name="Guardiola",
            email="pep.guardiola@example.com",
        )
        self.assertIsNotNone(coach.pk)
        self.assertIsNotNone(coach.public_id)
        self.assertIsNone(coach.certification)

    def test_str_representation(self):
        """Test __str__ returns full name."""
        self.assertEqual(str(self.coach), "Carlo Ancelotti")

    def test_public_id_generated_automatically(self):
        """Test that public_id is auto-generated."""
        self.assertIsNotNone(self.coach.public_id)
        self.assertGreater(len(self.coach.public_id), 0)

    def test_email_must_be_unique(self):
        """Test that duplicate emails raise IntegrityError."""
        with self.assertRaises(IntegrityError):
            Coach.objects.create(
                first_name="Fake",
                last_name="Ancelotti",
                email="carlo.ancelotti@example.com",
            )

    def test_certification_choices(self):
        """Test certification uses CoachingCertification enum."""
        self.assertEqual(
            self.coach.certification, CoachingCertification.ENTRENADOR_NACIONAL
        )

    def test_certification_nullable(self):
        """Test certification can be null."""
        coach = Coach.objects.create(
            first_name="Zinedine",
            last_name="Zidane",
            email="zidane@example.com",
        )
        self.assertIsNone(coach.certification)

    def test_all_certification_levels(self):
        """Test all certification levels can be assigned."""
        for i, cert in enumerate(CoachingCertification):
            coach = Coach.objects.create(
                first_name=f"Coach{i}",
                last_name="Test",
                email=f"coach{i}@example.com",
                certification=cert,
            )
            self.assertEqual(coach.certification, cert)

    def test_address_relationship(self):
        """Test coach can have an address."""
        self.assertEqual(self.coach.address, self.address)

    def test_address_set_null_on_delete(self):
        """Test that deleting address sets coach.address to null."""
        self.address.delete()
        self.coach.refresh_from_db()
        self.assertIsNone(self.coach.address)

    def test_auditory_fields_created(self):
        """Test that created_at and updated_at are set automatically."""
        self.assertIsNotNone(self.coach.created_at)
        self.assertIsNotNone(self.coach.updated_at)
