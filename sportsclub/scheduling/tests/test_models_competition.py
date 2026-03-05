# scheduling/tests/test_models_competition.py
from datetime import UTC, date, datetime

from core.models import Address
from django.test import TestCase
from inventory.models import Venue
from people.models import Athlete, Coach

from scheduling.models import Competition, Season


class CompetitionModelTest(TestCase):
    """Test suite for Competition model."""

    def setUp(self):
        """Set up test data."""
        self.season = Season.objects.create(
            name="2024-2025 Season",
            start_date=date(2024, 9, 1),
            end_date=date(2025, 6, 30),
        )
        self.address = Address.objects.create(
            line1="123 Stadium Way",
            city="Barcelona",
            postal_code="08001",
            country="ES",
        )
        self.venue = Venue.objects.create(
            name="Olympic Stadium",
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
        self.competition = Competition.objects.create(
            name="Spring Championship",
            date=datetime(2025, 4, 15, 10, 0, tzinfo=UTC),
            venue=self.venue,
            season=self.season,
        )
        self.competition.coaches.add(self.coach)
        self.competition.athletes.add(self.athlete)

    def test_create_competition(self):
        """Test creating a competition."""
        self.assertIsNotNone(self.competition.pk)
        self.assertIsNotNone(self.competition.public_id)

    def test_str_representation(self):
        """Test __str__ returns name."""
        self.assertEqual(str(self.competition), "Spring Championship (2025-04-15)")

    def test_season_relationship(self):
        """Test competition belongs to a season."""
        self.assertEqual(self.competition.season, self.season)

    def test_venue_relationship(self):
        """Test competition can have a venue."""
        self.assertEqual(self.competition.venue, self.venue)

    def test_venue_nullable(self):
        """Test competition can exist without venue."""
        competition = Competition.objects.create(
            name="Away Competition",
            date=datetime(2025, 5, 1, 10, 0, tzinfo=UTC),
            season=self.season,
        )
        self.assertIsNone(competition.venue)

    def test_venue_set_null_on_delete(self):
        """Test that deleting venue sets competition.venue to null."""
        self.venue.delete()
        self.competition.refresh_from_db()
        self.assertIsNone(self.competition.venue)

    def test_coaches_many_to_many(self):
        """Test competition can have multiple coaches."""
        coach2 = Coach.objects.create(
            first_name="Pep",
            last_name="Guardiola",
            email="pep@example.com",
            date_of_birth=date(1971, 1, 18),
        )
        self.competition.coaches.add(coach2)
        self.assertEqual(self.competition.coaches.count(), 2)

    def test_athletes_many_to_many(self):
        """Test competition can have multiple athletes."""
        athlete2 = Athlete.objects.create(
            first_name="Carl",
            last_name="Lewis",
            email="carl@example.com",
            date_of_birth=date(1961, 7, 1),
        )
        self.competition.athletes.add(athlete2)
        self.assertEqual(self.competition.athletes.count(), 2)

    def test_score_json_field(self):
        """Test score can store JSON data."""
        self.competition.score = {
            "results": {"sprints": {"gold": 2, "silver": 1, "bronze": 0}}
        }
        self.competition.save()
        self.competition.refresh_from_db()
        self.assertEqual(self.competition.score["results"]["sprints"]["gold"], 2)

    def test_score_nullable(self):
        """Test score can be null."""
        self.assertIsNone(self.competition.score)

    def test_cascade_delete_with_season(self):
        """Test that deleting season deletes competition."""
        competition_pk = self.competition.pk
        self.season.delete()
        self.assertFalse(Competition.objects.filter(pk=competition_pk).exists())

    def test_ordering_by_date_descending(self):
        """Test that competitions are ordered by date descending."""
        older_competition = Competition.objects.create(
            name="Winter Championship",
            date=datetime(2025, 1, 15, 10, 0, tzinfo=UTC),
            season=self.season,
        )
        competitions = list(Competition.objects.all())
        self.assertEqual(competitions[0], self.competition)
        self.assertEqual(competitions[1], older_competition)
