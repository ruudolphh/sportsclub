# scheduling/tests/test_api_trainings.py
import json
from datetime import UTC, date, datetime

from core.models import Address
from django.test import TestCase
from inventory.models import Venue
from people.models import Athlete, Coach

from scheduling.models import Season, Training


class TrainingAPITestCase(TestCase):
    """Test suite for Training API endpoints."""

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
            focus="Explosive starts",
        )
        self.training.coaches.add(self.coach)
        self.training.athletes.add(self.athlete)

    def test_list_trainings(self):
        """Test GET /api/v1/scheduling/trainings returns all trainings."""
        response = self.client.get("/api/v1/scheduling/trainings")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)

    def test_list_trainings_returns_expected_fields(self):
        """Test that list response contains expected fields."""
        response = self.client.get("/api/v1/scheduling/trainings")
        data = response.json()
        training = data[0]
        self.assertIn("public_id", training)
        self.assertIn("name", training)
        self.assertIn("date", training)
        self.assertIn("season", training)
        self.assertIn("focus", training)

    def test_get_training(self):
        """Test GET /api/v1/scheduling/trainings/{public_id} returns details."""
        response = self.client.get(
            f"/api/v1/scheduling/trainings/{self.training.public_id}"
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["name"], "Sprint Drills")
        self.assertEqual(data["focus"], "Explosive starts")
        self.assertIsNotNone(data["venue"])
        self.assertEqual(len(data["coaches"]), 1)
        self.assertEqual(len(data["athletes"]), 1)

    def test_get_training_not_found(self):
        """Test GET with non-existent public_id returns 404."""
        response = self.client.get("/api/v1/scheduling/trainings/nonexistent123")
        self.assertEqual(response.status_code, 404)

    def test_create_training_minimal(self):
        """Test POST /api/v1/scheduling/trainings with minimal data."""
        payload = {
            "name": "Endurance Training",
            "date": "2025-03-15T09:00:00Z",
            "season_public_id": self.season.public_id,
        }
        response = self.client.post(
            "/api/v1/scheduling/trainings",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["name"], "Endurance Training")
        self.assertEqual(data["focus"], "")
        self.assertIsNone(data["venue"])

    def test_create_training_full(self):
        """Test POST with all fields."""
        payload = {
            "name": "Technical Training",
            "date": "2025-03-20T09:00:00Z",
            "venue_public_id": self.venue.public_id,
            "season_public_id": self.season.public_id,
            "coach_public_ids": [self.coach.public_id],
            "athlete_public_ids": [self.athlete.public_id],
            "focus": "Hurdle technique",
        }
        response = self.client.post(
            "/api/v1/scheduling/trainings",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["name"], "Technical Training")
        self.assertEqual(data["focus"], "Hurdle technique")
        self.assertIsNotNone(data["venue"])
        self.assertEqual(len(data["coaches"]), 1)

    def test_create_training_invalid_season(self):
        """Test POST with non-existent season returns 404."""
        payload = {
            "name": "Invalid Training",
            "date": "2025-03-15T09:00:00Z",
            "season_public_id": "nonexistent123",
        }
        response = self.client.post(
            "/api/v1/scheduling/trainings",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 404)

    def test_update_training_put(self):
        """Test PUT /api/v1/scheduling/trainings/{public_id} fully updates."""
        payload = {
            "name": "Updated Training",
            "date": "2025-03-25T10:00:00Z",
            "season_public_id": self.season.public_id,
            "focus": "New focus",
        }
        response = self.client.put(
            f"/api/v1/scheduling/trainings/{self.training.public_id}",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["name"], "Updated Training")
        self.assertEqual(data["focus"], "New focus")
        self.assertIsNone(data["venue"])  # PUT without venue clears it
        self.assertEqual(len(data["coaches"]), 0)  # PUT without coaches clears them

    def test_partial_update_training_patch(self):
        """Test PATCH /api/v1/scheduling/trainings/{public_id} partially updates."""
        payload = {"focus": "Updated focus"}
        response = self.client.patch(
            f"/api/v1/scheduling/trainings/{self.training.public_id}",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["focus"], "Updated focus")
        self.assertEqual(data["name"], "Sprint Drills")  # Unchanged
        self.assertIsNotNone(data["venue"])  # Unchanged
        self.assertEqual(len(data["coaches"]), 1)  # Unchanged

    def test_patch_training_clear_venue(self):
        """Test PATCH to clear venue."""
        payload = {"venue_public_id": None}
        response = self.client.patch(
            f"/api/v1/scheduling/trainings/{self.training.public_id}",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsNone(data["venue"])

    def test_delete_training(self):
        """Test DELETE /api/v1/scheduling/trainings/{public_id} removes training."""
        response = self.client.delete(
            f"/api/v1/scheduling/trainings/{self.training.public_id}"
        )
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Training.objects.filter(pk=self.training.pk).exists())

    def test_delete_training_not_found(self):
        """Test DELETE with non-existent public_id returns 404."""
        response = self.client.delete("/api/v1/scheduling/trainings/nonexistent123")
        self.assertEqual(response.status_code, 404)
