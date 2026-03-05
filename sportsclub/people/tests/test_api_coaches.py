# people/tests/test_api_coaches.py
import json

from core.models import Address
from django.test import TestCase

from people.models import Coach, CoachingCertification


class CoachAPITestCase(TestCase):
    """Test suite for Coach API endpoints."""

    def setUp(self):
        """Set up test data."""
        self.address = Address.objects.create(
            line1="456 Stadium Road",
            city="Madrid",
            postal_code="28001",
            country="ES",
        )
        self.coach1 = Coach.objects.create(
            first_name="Carlo",
            last_name="Ancelotti",
            email="carlo.ancelotti@example.com",
            phone="+1234567890",
            certification=CoachingCertification.ENTRENADOR_NACIONAL,
            address=self.address,
        )
        self.coach2 = Coach.objects.create(
            first_name="Pep",
            last_name="Guardiola",
            email="pep.guardiola@example.com",
            certification=CoachingCertification.TECNICO_DEPORTIVO_GRADO_SUPERIOR,
        )

    def test_list_coaches(self):
        """Test GET /api/v1/people/coaches returns all coaches."""
        response = self.client.get("/api/v1/people/coaches")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 2)

    def test_list_coaches_returns_expected_fields(self):
        """Test that list response contains only list fields."""
        response = self.client.get("/api/v1/people/coaches")
        data = response.json()
        coach = data[0]
        self.assertIn("public_id", coach)
        self.assertIn("first_name", coach)
        self.assertIn("last_name", coach)
        self.assertIn("certification", coach)
        self.assertNotIn("email", coach)
        self.assertNotIn("address", coach)

    def test_get_coach(self):
        """Test GET /api/v1/people/coaches/{public_id} returns coach details."""
        response = self.client.get(f"/api/v1/people/coaches/{self.coach1.public_id}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["first_name"], "Carlo")
        self.assertEqual(
            data["certification"], CoachingCertification.ENTRENADOR_NACIONAL
        )
        self.assertIsNotNone(data["address"])

    def test_get_coach_not_found(self):
        """Test GET with non-existent public_id returns 404."""
        response = self.client.get("/api/v1/people/coaches/nonexistent123")
        self.assertEqual(response.status_code, 404)

    def test_create_coach_minimal(self):
        """Test POST /api/v1/people/coaches with minimal data."""
        payload = {
            "first_name": "Zinedine",
            "last_name": "Zidane",
            "email": "zidane@example.com",
        }
        response = self.client.post(
            "/api/v1/people/coaches",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["first_name"], "Zinedine")
        self.assertIsNone(data["certification"])

    def test_create_coach_full(self):
        """Test POST with all fields."""
        payload = {
            "first_name": "Zinedine",
            "last_name": "Zidane",
            "email": "zidane@example.com",
            "phone": "+33123456789",
            "date_of_birth": "1972-06-23",
            "address_public_id": self.address.public_id,
            "certification": CoachingCertification.ENTRENADOR_NACIONAL,
        }
        response = self.client.post(
            "/api/v1/people/coaches",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(
            data["certification"], CoachingCertification.ENTRENADOR_NACIONAL
        )
        self.assertIsNotNone(data["address"])

    def test_create_coach_invalid_certification(self):
        """Test POST with invalid certification returns 422."""
        payload = {
            "first_name": "Zinedine",
            "last_name": "Zidane",
            "email": "zidane@example.com",
            "certification": "INVALID",
        }
        response = self.client.post(
            "/api/v1/people/coaches",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 422)

    def test_update_coach_put(self):
        """Test PUT /api/v1/people/coaches/{public_id} fully updates coach."""
        payload = {
            "first_name": "Carlo",
            "last_name": "Ancelotti-Updated",
            "email": "carlo.updated@example.com",
            "certification": CoachingCertification.ENTRENADOR_CLUB,
        }
        response = self.client.put(
            f"/api/v1/people/coaches/{self.coach1.public_id}",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["last_name"], "Ancelotti-Updated")
        self.assertEqual(data["certification"], CoachingCertification.ENTRENADOR_CLUB)
        self.assertIsNone(data["address"])  # PUT without address clears it

    def test_partial_update_coach_patch(self):
        """Test PATCH /api/v1/people/coaches/{public_id} partially updates coach."""
        payload = {"certification": CoachingCertification.ENTRENADOR_CLUB}
        response = self.client.patch(
            f"/api/v1/people/coaches/{self.coach1.public_id}",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["certification"], CoachingCertification.ENTRENADOR_CLUB)
        self.assertEqual(data["first_name"], "Carlo")  # Unchanged
        self.assertIsNotNone(data["address"])  # Unchanged

    def test_delete_coach(self):
        """Test DELETE /api/v1/people/coaches/{public_id} removes coach."""
        response = self.client.delete(f"/api/v1/people/coaches/{self.coach1.public_id}")
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Coach.objects.filter(pk=self.coach1.pk).exists())

    def test_delete_coach_not_found(self):
        """Test DELETE with non-existent public_id returns 404."""
        response = self.client.delete("/api/v1/people/coaches/nonexistent123")
        self.assertEqual(response.status_code, 404)
