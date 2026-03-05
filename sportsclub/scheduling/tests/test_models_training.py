# scheduling/tests/test_models_training.py
from datetime import UTC, date, datetime

from core.models import Address
from django.test import TestCase
from inventory.models import Venue
from people.models import Athlete, Coach

from scheduling.models import Season, Training


class TrainingModelTest(TestCase):
    """Test suite for Training model."""

    def setUp(self):
        """Set up test data."""
        self.season = Season.objects.create(
            name="2024-2025 Season",
            start_date=date(2024, 9, 1),
            end_date=date(2025, 6, 30),
        )
        self.address = Address.objects.create(
            line1="456 Training Center",
            city="Madrid",
            postal_code="28001",
            country="ES",
        )
        self.venue = Venue.objects.create(
            name="Training Facility",
            address=self.address,
        )
        self.coach = Coach.objects.create(
            first_name="Carlo",
            last_name="Ancelotti",
            email="carlo@example.com",
            date_of_birth=date(1959, 6, 10),
        )
        self.athlete = Athlete.objects.create(
            first_name="Usain",
            last_name="Bolt",
            email="usain@example.com",
            date_of_birth=date(1986, 8, 21),
        )
        self.training = Training.objects.create(
            name="Sprint Drills",
            date=datetime(2025, 3, 10, 9, 0, tzinfo=UTC),
            venue=self.venue,
            season=self.season,
            focus="Explosive starts and acceleration",
        )
        self.training.coaches.add(self.coach)
        self.training.athletes.add(self.athlete)

    def test_create_training(self):
        """Test creating a training session."""
        self.assertIsNotNone(self.training.pk)
        self.assertIsNotNone(self.training.public_id)

    def test_str_representation(self):
        """Test __str__ returns name."""
        self.assertEqual(str(self.training), "Sprint Drills (2025-03-10)")

    def test_focus_field(self):
        """Test training has focus field."""
        self.assertEqual(self.training.focus, "Explosive starts and acceleration")

    def test_focus_can_be_blank(self):
        """Test focus field can be blank."""
        training = Training.objects.create(
            name="General Practice",
            date=datetime(2025, 3, 11, 9, 0, tzinfo=UTC),
            season=self.season,
        )
        self.assertEqual(training.focus, "")

    def test_season_relationship(self):
        """Test training belongs to a season."""
        self.assertEqual(self.training.season, self.season)

    def test_venue_relationship(self):
        """Test training can have a venue."""
        self.assertEqual(self.training.venue, self.venue)

    def test_venue_nullable(self):
        """Test training can exist without venue."""
        training = Training.objects.create(
            name="Outdoor Training",
            date=datetime(2025, 3, 12, 9, 0, tzinfo=UTC),
            season=self.season,
        )
        self.assertIsNone(training.venue)

    def test_coaches_many_to_many(self):
        """Test training can have multiple coaches."""
        coach2 = Coach.objects.create(
            first_name="Pep",
            last_name="Guardiola",
            email="pep@example.com",
            date_of_birth=date(1971, 1, 18),
        )
        self.training.coaches.add(coach2)
        self.assertEqual(self.training.coaches.count(), 2)

    def test_athletes_many_to_many(self):
        """Test training can have multiple athletes."""
        athlete2 = Athlete.objects.create(
            first_name="Carl",
            last_name="Lewis",
            email="carl@example.com",
            date_of_birth=date(1961, 7, 1),
        )
        self.training.athletes.add(athlete2)
        self.assertEqual(self.training.athletes.count(), 2)

    def test_cascade_delete_with_season(self):
        """Test that deleting season deletes training."""
        training_pk = self.training.pk
        self.season.delete()
        self.assertFalse(Training.objects.filter(pk=training_pk).exists())
