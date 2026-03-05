# inventory/tests/test_api_venues.py
"""API integration tests for Venue endpoints."""

import json

from core.models import Address
from django.test import TestCase

from inventory.models import Venue, VenueType


class VenueAPITestCase(TestCase):
    """Test suite for Venue API endpoints."""

    def setUp(self):
        """Set up sample data before each test."""
        self.address = Address.objects.create(
            line1="Carrer de les Corts, 1",
            city="Barcelona",
            state="Catalunya",
            country="Spain",
        )

        self.venue1 = Venue.objects.create(
            name="Camp Nou",
            venue_type=VenueType.STADIUM,
            capacity=99354,
            address=self.address,
            indoor=False,
        )

        self.venue2 = Venue.objects.create(
            name="Palau Blaugrana",
            venue_type=VenueType.GYMNASIUM,
            capacity=7585,
            indoor=True,
        )

    def test_list_venues(self):
        """Test GET /api/v1/inventory/venues."""
        response = self.client.get("/api/v1/inventory/venues")

        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 2)

        first_venue = data[0]
        self.assertIn("public_id", first_venue)
        self.assertIn("name", first_venue)
        self.assertIn("venue_type", first_venue)
        self.assertIn("indoor", first_venue)

    def test_get_venue_by_id(self):
        """Test GET /api/v1/inventory/venues/{public_id}."""
        response = self.client.get(f"/api/v1/inventory/venues/{self.venue1.public_id}")

        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data["public_id"], self.venue1.public_id)
        self.assertEqual(data["name"], "Camp Nou")
        self.assertEqual(data["venue_type"], VenueType.STADIUM)
        self.assertEqual(data["capacity"], 99354)
        self.assertFalse(data["indoor"])
        self.assertIsNotNone(data["address"])
        self.assertEqual(data["address"]["city"], "Barcelona")

    def test_get_venue_without_address(self):
        """Test GET venue that has no address."""
        response = self.client.get(f"/api/v1/inventory/venues/{self.venue2.public_id}")

        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data["name"], "Palau Blaugrana")
        self.assertIsNone(data["address"])

    def test_get_venue_not_found(self):
        """Test GET /api/v1/inventory/venues/{public_id} with non-existent ID."""
        response = self.client.get("/api/v1/inventory/venues/nonexistent123")
        self.assertEqual(response.status_code, 404)

    def test_create_venue_minimal(self):
        """Test POST /api/v1/inventory/venues with minimal data."""
        payload = {"name": "Local Track"}

        response = self.client.post(
            "/api/v1/inventory/venues",
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)

        data = response.json()
        self.assertIn("public_id", data)
        self.assertEqual(data["name"], "Local Track")
        self.assertEqual(data["venue_type"], VenueType.FIELD)  # Default
        self.assertIsNone(data["capacity"])
        self.assertFalse(data["indoor"])

        self.assertEqual(Venue.objects.count(), 3)

    def test_create_venue_full(self):
        """Test POST /api/v1/inventory/venues with all fields."""
        payload = {
            "name": "Estadi Olímpic",
            "venue_type": VenueType.STADIUM,
            "capacity": 55926,
            "address_public_id": self.address.public_id,
            "indoor": False,
        }

        response = self.client.post(
            "/api/v1/inventory/venues",
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)

        data = response.json()
        self.assertEqual(data["name"], "Estadi Olímpic")
        self.assertEqual(data["venue_type"], VenueType.STADIUM)
        self.assertEqual(data["capacity"], 55926)
        self.assertIsNotNone(data["address"])
        self.assertEqual(data["address"]["public_id"], self.address.public_id)

    def test_create_venue_invalid_address(self):
        """Test POST with non-existent address_public_id returns 404."""
        payload = {
            "name": "Test Venue",
            "address_public_id": "nonexistent123",
        }

        response = self.client.post(
            "/api/v1/inventory/venues",
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 404)

    def test_create_venue_without_name(self):
        """Test POST without required name field returns 422."""
        payload = {"venue_type": VenueType.STADIUM}

        response = self.client.post(
            "/api/v1/inventory/venues",
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 422)

    def test_create_venue_with_empty_name(self):
        """Test POST with empty name returns 422."""
        payload = {"name": ""}

        response = self.client.post(
            "/api/v1/inventory/venues",
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 422)

    def test_create_venue_with_negative_capacity(self):
        """Test POST with negative capacity returns 422."""
        payload = {"name": "Test Venue", "capacity": -100}

        response = self.client.post(
            "/api/v1/inventory/venues",
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 422)

    def test_update_venue_put(self):
        """Test PUT /api/v1/inventory/venues/{public_id}."""
        payload = {
            "name": "Camp Nou Renovat",
            "venue_type": VenueType.STADIUM,
            "capacity": 105000,
            "address_public_id": self.address.public_id,
            "indoor": False,
        }

        response = self.client.put(
            f"/api/v1/inventory/venues/{self.venue1.public_id}",
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data["name"], "Camp Nou Renovat")
        self.assertEqual(data["capacity"], 105000)

        self.venue1.refresh_from_db()
        self.assertEqual(self.venue1.name, "Camp Nou Renovat")
        self.assertEqual(self.venue1.capacity, 105000)

    def test_update_venue_put_clears_address(self):
        """Test PUT without address_public_id clears the address."""
        payload = {
            "name": "Camp Nou",
            "venue_type": VenueType.STADIUM,
            "capacity": 99354,
            "indoor": False,
        }

        response = self.client.put(
            f"/api/v1/inventory/venues/{self.venue1.public_id}",
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIsNone(data["address"])

        self.venue1.refresh_from_db()
        self.assertIsNone(self.venue1.address)

    def test_update_venue_put_not_found(self):
        """Test PUT with non-existent ID returns 404."""
        payload = {"name": "Test Venue"}

        response = self.client.put(
            "/api/v1/inventory/venues/nonexistent123",
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 404)

    def test_partial_update_venue_patch(self):
        """Test PATCH /api/v1/inventory/venues/{public_id}."""
        original_capacity = self.venue1.capacity

        payload = {"name": "Camp Nou Actualitzat"}

        response = self.client.patch(
            f"/api/v1/inventory/venues/{self.venue1.public_id}",
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data["name"], "Camp Nou Actualitzat")
        self.assertEqual(data["capacity"], original_capacity)  # Unchanged

        self.venue1.refresh_from_db()
        self.assertEqual(self.venue1.name, "Camp Nou Actualitzat")
        self.assertEqual(self.venue1.capacity, original_capacity)

    def test_patch_venue_address(self):
        """Test PATCH to change venue address."""
        new_address = Address.objects.create(
            line1="Avinguda Joan XXIII, s/n",
            city="Barcelona",
            country="Spain",
        )

        payload = {"address_public_id": new_address.public_id}

        response = self.client.patch(
            f"/api/v1/inventory/venues/{self.venue1.public_id}",
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data["address"]["public_id"], new_address.public_id)

        self.venue1.refresh_from_db()
        self.assertEqual(self.venue1.address, new_address)

    def test_patch_venue_clear_address(self):
        """Test PATCH to clear venue address with explicit null."""
        payload = {"address_public_id": None}

        response = self.client.patch(
            f"/api/v1/inventory/venues/{self.venue1.public_id}",
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIsNone(data["address"])

        self.venue1.refresh_from_db()
        self.assertIsNone(self.venue1.address)

    def test_patch_multiple_fields(self):
        """Test PATCH updating multiple fields at once."""
        payload = {
            "name": "Nou Camp Nou",
            "capacity": 110000,
            "indoor": True,
        }

        response = self.client.patch(
            f"/api/v1/inventory/venues/{self.venue1.public_id}",
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)

        self.venue1.refresh_from_db()
        self.assertEqual(self.venue1.name, "Nou Camp Nou")
        self.assertEqual(self.venue1.capacity, 110000)
        self.assertTrue(self.venue1.indoor)

    def test_delete_venue(self):
        """Test DELETE /api/v1/inventory/venues/{public_id}."""
        venue_public_id = self.venue1.public_id

        response = self.client.delete(f"/api/v1/inventory/venues/{venue_public_id}")

        self.assertEqual(response.status_code, 204)

        self.assertFalse(Venue.objects.filter(public_id=venue_public_id).exists())
        self.assertEqual(Venue.objects.count(), 1)

    def test_delete_venue_not_found(self):
        """Test DELETE with non-existent ID returns 404."""
        response = self.client.delete("/api/v1/inventory/venues/nonexistent123")
        self.assertEqual(response.status_code, 404)

    def test_delete_venue_preserves_address(self):
        """Test that deleting a venue does not delete its address."""
        address_public_id = self.address.public_id

        response = self.client.delete(
            f"/api/v1/inventory/venues/{self.venue1.public_id}"
        )

        self.assertEqual(response.status_code, 204)

        # Address should still exist
        self.assertTrue(Address.objects.filter(public_id=address_public_id).exists())
