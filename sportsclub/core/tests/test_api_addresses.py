# core/tests/test_api_addresses.py
"""API integration tests for Address endpoints."""

import json

from django.test import TestCase

from core.models import Address


class AddressAPITestCase(TestCase):
    """
    Test suite for Address API endpoints.

    Uses Django's built-in test client with full URL paths (/api/v1/...).
    """

    def setUp(self):
        """Set up sample data before each test."""
        self.address1 = Address.objects.create(
            line1="Av. de Jaume III, 15",
            line2="Centre",
            postal_code="07012",
            city="Palma",
            state="Illes Balears",
            country="Spain",
        )

        self.address2 = Address.objects.create(
            line1="Plaça de la Porta de Santa Catalina, 10",
            postal_code="07012",
            city="Palma",
            state="Illes Balears",
            country="Spain",
        )

    def test_list_addresses(self):
        """Test GET /api/v1/core/addresses."""
        response = self.client.get("/api/v1/core/addresses")

        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 2)

        first_address = data[0]
        self.assertIn("public_id", first_address)
        self.assertIn("formatted_address", first_address)

    def test_get_address_by_id(self):
        """Test GET /api/v1/core/addresses/{public_id}."""
        response = self.client.get(f"/api/v1/core/addresses/{self.address1.public_id}")

        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data["public_id"], self.address1.public_id)
        self.assertEqual(data["line1"], "Av. de Jaume III, 15")
        self.assertEqual(data["city"], "Palma")
        self.assertEqual(data["country"], "Spain")
        self.assertIn("line2", data)
        self.assertIn("postal_code", data)
        self.assertIn("state", data)

    def test_get_address_by_id_not_found(self):
        """Test GET /api/v1/core/addresses/{public_id} with non-existent ID."""
        response = self.client.get("/api/v1/core/addresses/nonexistent123")
        self.assertEqual(response.status_code, 404)

    def test_create_address(self):
        """Test POST /api/v1/core/addresses."""
        payload = {
            "line1": "Ctra. de Montjuïc, 66",
            "line2": "Sants-Montjuïc",
            "postal_code": "08038",
            "city": "Barcelona",
            "state": "Barcelona",
            "country": "Spain",
        }

        response = self.client.post(
            "/api/v1/core/addresses",
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)

        data = response.json()
        self.assertIn("public_id", data)
        self.assertEqual(data["line1"], "Ctra. de Montjuïc, 66")
        self.assertEqual(data["city"], "Barcelona")

        self.assertTrue(Address.objects.filter(line1="Ctra. de Montjuïc, 66").exists())
        self.assertEqual(Address.objects.count(), 3)

    def test_create_address_minimal(self):
        """Test POST /api/v1/core/addresses with only required fields."""
        payload = {"line1": "Carrer de la Feixa Llarga, s/n"}

        response = self.client.post(
            "/api/v1/core/addresses",
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)

        data = response.json()
        self.assertEqual(data["line1"], "Carrer de la Feixa Llarga, s/n")
        self.assertEqual(data["line2"], "")
        self.assertEqual(data["city"], "")

    def test_create_address_without_required_field_line1(self):
        """Test POST /api/v1/core/addresses without required field line1."""
        payload = {"line2": "L'Eixample"}

        response = self.client.post(
            "/api/v1/core/addresses",
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 422)

    def test_create_address_with_very_long_line1(self):
        """Test POST /api/v1/core/addresses with line1 exceeding max_length."""
        payload = {"line1": "x" * 300}

        response = self.client.post(
            "/api/v1/core/addresses",
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 422)

    def test_update_address_put(self):
        """Test PUT /api/v1/core/addresses/{public_id}."""
        payload = {
            "line1": "Av. Pío Baroja, 3",
            "line2": "Campanar",
            "postal_code": "46015",
            "city": "València",
            "state": "Valencia",
            "country": "Spain",
        }

        response = self.client.put(
            f"/api/v1/core/addresses/{self.address1.public_id}",
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data["line1"], "Av. Pío Baroja, 3")
        self.assertEqual(data["city"], "València")

        self.address1.refresh_from_db()
        self.assertEqual(self.address1.line1, "Av. Pío Baroja, 3")
        self.assertEqual(self.address1.city, "València")

    def test_update_address_put_not_found(self):
        """Test PUT /api/v1/core/addresses/{public_id} with non-existent ID."""
        payload = {"line1": "Quatre Carreres"}

        response = self.client.put(
            "/api/v1/core/addresses/nonexistent123",
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 404)

    def test_partial_update_address_patch(self):
        """Test PATCH /api/v1/core/addresses/{public_id}."""
        original_line1 = self.address1.line1
        original_postal_code = self.address1.postal_code

        payload = {"city": "Sevilla"}

        response = self.client.patch(
            f"/api/v1/core/addresses/{self.address1.public_id}",
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data["city"], "Sevilla")

        self.address1.refresh_from_db()
        self.assertEqual(self.address1.city, "Sevilla")
        self.assertEqual(self.address1.line1, original_line1)
        self.assertEqual(self.address1.postal_code, original_postal_code)

    def test_patch_multiple_fields(self):
        """Test PATCH /api/v1/core/addresses/{public_id} with multiple fields."""
        payload = {"city": "Bilbao", "postal_code": "48001"}

        response = self.client.patch(
            f"/api/v1/core/addresses/{self.address1.public_id}",
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)

        self.address1.refresh_from_db()
        self.assertEqual(self.address1.city, "Bilbao")
        self.assertEqual(self.address1.postal_code, "48001")

    def test_delete_address(self):
        """Test DELETE /api/v1/core/addresses/{public_id}."""
        address_public_id = self.address1.public_id

        response = self.client.delete(f"/api/v1/core/addresses/{address_public_id}")

        self.assertEqual(response.status_code, 204)

        self.assertFalse(Address.objects.filter(public_id=address_public_id).exists())
        self.assertEqual(Address.objects.count(), 1)

    def test_delete_address_not_found(self):
        """Test DELETE /api/v1/core/addresses/{public_id} with non-existent ID."""
        response = self.client.delete("/api/v1/core/addresses/nonexistent123")
        self.assertEqual(response.status_code, 404)
