# people/tests/test_api_athletes.py
import json

from core.models import Address
from django.test import TestCase

from people.models import Athlete


class AthleteAPITestCase(TestCase):
    """Test suite for Athlete API endpoints."""

    def setUp(self):
        """Set up test data."""
        self.address = Address.objects.create(
            line1="123 Track Lane",
            line2="Olympic Village",
            city="Barcelona",
            state="Catalonia",
            postal_code="08001",
            country="ES",
        )
        self.athlete1 = Athlete.objects.create(
            first_name="Usain",
            last_name="Bolt",
            email="usain.bolt@example.com",
            phone="+1234567890",
            height=195.0,
            weight=94.0,
            jersey_number=9,
            address=self.address,
        )
        self.athlete2 = Athlete.objects.create(
            first_name="Carl",
            last_name="Lewis",
            email="carl.lewis@example.com",
            jersey_number=15,
        )

    def test_list_athletes(self):
        """Test GET /api/v1/people/athletes returns all athletes."""
        response = self.client.get("/api/v1/people/athletes")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 2)

    def test_list_athletes_returns_expected_fields(self):
        """Test that list response contains only list fields."""
        response = self.client.get("/api/v1/people/athletes")
        data = response.json()
        athlete = data[0]
        self.assertIn("public_id", athlete)
        self.assertIn("first_name", athlete)
        self.assertIn("last_name", athlete)
        self.assertIn("jersey_number", athlete)
        self.assertNotIn("email", athlete)
        self.assertNotIn("height", athlete)

    def test_get_athlete(self):
        """Test GET /api/v1/people/athletes/{public_id} returns athlete details."""
        response = self.client.get(f"/api/v1/people/athletes/{self.athlete1.public_id}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["first_name"], "Usain")
        self.assertEqual(data["last_name"], "Bolt")
        self.assertEqual(data["email"], "usain.bolt@example.com")
        self.assertEqual(data["height"], 195.0)
        self.assertIsNotNone(data["address"])
        self.assertEqual(data["address"]["city"], "Barcelona")

    def test_get_athlete_not_found(self):
        """Test GET with non-existent public_id returns 404."""
        response = self.client.get("/api/v1/people/athletes/nonexistent123")
        self.assertEqual(response.status_code, 404)

    def test_create_athlete_minimal(self):
        """Test POST /api/v1/people/athletes with minimal data."""
        payload = {
            "first_name": "Florence",
            "last_name": "Griffith",
            "email": "flo.jo@example.com",
        }
        response = self.client.post(
            "/api/v1/people/athletes",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["first_name"], "Florence")
        self.assertEqual(data["email"], "flo.jo@example.com")
        self.assertIsNone(data["address"])

    def test_create_athlete_full(self):
        """Test POST with all fields including address."""
        payload = {
            "first_name": "Florence",
            "last_name": "Griffith",
            "email": "flo.jo@example.com",
            "phone": "+1987654321",
            "date_of_birth": "1959-12-21",
            "address_public_id": self.address.public_id,
            "height": 170.0,
            "weight": 57.0,
            "jersey_number": 21,
        }
        response = self.client.post(
            "/api/v1/people/athletes",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["height"], 170.0)
        self.assertIsNotNone(data["address"])

    def test_create_athlete_invalid_address(self):
        """Test POST with non-existent address_public_id returns 404."""
        payload = {
            "first_name": "Florence",
            "last_name": "Griffith",
            "email": "flo.jo@example.com",
            "address_public_id": "nonexistent123",
        }
        response = self.client.post(
            "/api/v1/people/athletes",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 404)

    def test_create_athlete_invalid_email(self):
        """Test POST with invalid email returns 422."""
        payload = {
            "first_name": "Florence",
            "last_name": "Griffith",
            "email": "not-an-email",
        }
        response = self.client.post(
            "/api/v1/people/athletes",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 422)

    def test_create_athlete_duplicate_email(self):
        """Test POST with duplicate email returns 409 Conflict."""
        payload = {
            "first_name": "Another",
            "last_name": "Athlete",
            "email": "usain.bolt@example.com",  # Already exists
        }
        response = self.client.post(
            "/api/v1/people/athletes",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 409)

    def test_update_athlete_put(self):
        """Test PUT /api/v1/people/athletes/{public_id} fully updates athlete."""
        payload = {
            "first_name": "Usain",
            "last_name": "Bolt-Updated",
            "email": "usain.updated@example.com",
            "phone": "+9999999999",
            "height": 196.0,
            "weight": 95.0,
            "jersey_number": 10,
        }
        response = self.client.put(
            f"/api/v1/people/athletes/{self.athlete1.public_id}",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["last_name"], "Bolt-Updated")
        self.assertEqual(data["height"], 196.0)
        self.assertIsNone(data["address"])  # PUT without address clears it

    def test_update_athlete_put_with_address(self):
        """Test PUT with address_public_id sets address."""
        payload = {
            "first_name": "Carl",
            "last_name": "Lewis",
            "email": "carl.lewis@example.com",
            "address_public_id": self.address.public_id,
        }
        response = self.client.put(
            f"/api/v1/people/athletes/{self.athlete2.public_id}",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsNotNone(data["address"])

    def test_partial_update_athlete_patch(self):
        """Test PATCH /api/v1/people/athletes/{public_id} partially updates athlete."""
        payload = {"jersey_number": 99}
        response = self.client.patch(
            f"/api/v1/people/athletes/{self.athlete1.public_id}",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["jersey_number"], 99)
        self.assertEqual(data["first_name"], "Usain")  # Unchanged
        self.assertIsNotNone(data["address"])  # Unchanged

    def test_patch_athlete_clear_address(self):
        """Test PATCH with null address_public_id clears address."""
        payload = {"address_public_id": None}
        response = self.client.patch(
            f"/api/v1/people/athletes/{self.athlete1.public_id}",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsNone(data["address"])

    def test_delete_athlete(self):
        """Test DELETE /api/v1/people/athletes/{public_id} removes athlete."""
        response = self.client.delete(
            f"/api/v1/people/athletes/{self.athlete1.public_id}"
        )
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Athlete.objects.filter(pk=self.athlete1.pk).exists())

    def test_delete_athlete_not_found(self):
        """Test DELETE with non-existent public_id returns 404."""
        response = self.client.delete("/api/v1/people/athletes/nonexistent123")
        self.assertEqual(response.status_code, 404)
