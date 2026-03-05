# scheduling/tests/test_api_competitions.py
import json
from datetime import UTC, date, datetime

from core.models import Address
from django.test import TestCase
from inventory.models import Venue
from people.models import Athlete, Coach

from scheduling.models import Competition, Season


class CompetitionAPITestCase(TestCase):
    """Test suite for Competition API endpoints."""

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

    def test_list_competitions(self):
        """Test GET /api/v1/scheduling/competitions returns all competitions."""
        response = self.client.get("/api/v1/scheduling/competitions")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)

    def test_list_competitions_returns_expected_fields(self):
        """Test that list response contains expected fields."""
        response = self.client.get("/api/v1/scheduling/competitions")
        data = response.json()
        competition = data[0]
        self.assertIn("public_id", competition)
        self.assertIn("name", competition)
        self.assertIn("date", competition)
        self.assertIn("season", competition)

    def test_get_competition(self):
        """Test GET /api/v1/scheduling/competitions/{public_id} returns details."""
        response = self.client.get(
            f"/api/v1/scheduling/competitions/{self.competition.public_id}"
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["name"], "Spring Championship")
        self.assertIsNotNone(data["venue"])
        self.assertEqual(data["venue"]["name"], "Olympic Stadium")
        self.assertEqual(len(data["coaches"]), 1)
        self.assertEqual(len(data["athletes"]), 1)

    def test_get_competition_not_found(self):
        """Test GET with non-existent public_id returns 404."""
        response = self.client.get("/api/v1/scheduling/competitions/nonexistent123")
        self.assertEqual(response.status_code, 404)

    def test_create_competition_minimal(self):
        """Test POST /api/v1/scheduling/competitions with minimal data."""
        payload = {
            "name": "Winter Championship",
            "date": "2025-01-15T10:00:00Z",
            "season_public_id": self.season.public_id,
        }
        response = self.client.post(
            "/api/v1/scheduling/competitions",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["name"], "Winter Championship")
        self.assertIsNone(data["venue"])

    def test_create_competition_full(self):
        """Test POST with all fields."""
        payload = {
            "name": "Summer Championship",
            "date": "2025-07-15T10:00:00Z",
            "venue_public_id": self.venue.public_id,
            "season_public_id": self.season.public_id,
            "coach_public_ids": [self.coach.public_id],
            "athlete_public_ids": [self.athlete.public_id],
            "score": {"results": {"sprints": {"gold": 2, "silver": 1, "bronze": 0}}},
        }
        response = self.client.post(
            "/api/v1/scheduling/competitions",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["name"], "Summer Championship")
        self.assertIsNotNone(data["venue"])
        self.assertEqual(len(data["coaches"]), 1)
        self.assertIsNotNone(data["score"])

    def test_create_competition_invalid_season(self):
        """Test POST with non-existent season returns 404."""
        payload = {
            "name": "Invalid Competition",
            "date": "2025-01-15T10:00:00Z",
            "season_public_id": "nonexistent123",
        }
        response = self.client.post(
            "/api/v1/scheduling/competitions",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 404)

    def test_update_competition_put(self):
        """Test PUT /api/v1/scheduling/competitions/{public_id} fully updates."""
        payload = {
            "name": "Updated Championship",
            "date": "2025-05-01T14:00:00Z",
            "season_public_id": self.season.public_id,
        }
        response = self.client.put(
            f"/api/v1/scheduling/competitions/{self.competition.public_id}",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["name"], "Updated Championship")
        self.assertIsNone(data["venue"])  # PUT without venue clears it
        self.assertEqual(len(data["coaches"]), 0)  # PUT without coaches clears them

    def test_partial_update_competition_patch(self):
        """Test PATCH /api/v1/scheduling/competitions/{public_id} partially updates."""
        payload = {"name": "Partially Updated Championship"}
        response = self.client.patch(
            f"/api/v1/scheduling/competitions/{self.competition.public_id}",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["name"], "Partially Updated Championship")
        self.assertIsNotNone(data["venue"])  # Unchanged
        self.assertEqual(len(data["coaches"]), 1)  # Unchanged

    def test_patch_competition_update_score(self):
        """Test PATCH to update score."""
        payload = {
            "score": {"results": {"high_jump": {"gold": 1, "silver": 2, "bronze": 3}}}
        }
        response = self.client.patch(
            f"/api/v1/scheduling/competitions/{self.competition.public_id}",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsNotNone(data["score"])
        self.assertEqual(data["score"]["results"]["high_jump"]["gold"], 1)

    def test_delete_competition(self):
        """Test DELETE /api/v1/scheduling/competitions/{public_id} removes competition."""  # noqa: E501
        response = self.client.delete(
            f"/api/v1/scheduling/competitions/{self.competition.public_id}"
        )
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Competition.objects.filter(pk=self.competition.pk).exists())

    def test_delete_competition_not_found(self):
        """Test DELETE with non-existent public_id returns 404."""
        response = self.client.delete("/api/v1/scheduling/competitions/nonexistent123")
        self.assertEqual(response.status_code, 404)
