# scheduling/tests/test_api_seasons.py
import json
from datetime import date

from django.test import TestCase

from scheduling.models import Season


class SeasonAPITestCase(TestCase):
    """Test suite for Season API endpoints."""

    def setUp(self):
        """Set up test data."""
        self.season1 = Season.objects.create(
            name="2024-2025 Season",
            start_date=date(2024, 9, 1),
            end_date=date(2025, 6, 30),
        )
        self.season2 = Season.objects.create(
            name="2023-2024 Season",
            start_date=date(2023, 9, 1),
            end_date=date(2024, 6, 30),
        )

    def test_list_seasons(self):
        """Test GET /api/v1/scheduling/seasons returns all seasons."""
        response = self.client.get("/api/v1/scheduling/seasons")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 2)

    def test_list_seasons_ordered_by_start_date_desc(self):
        """Test that seasons are ordered by start_date descending."""
        response = self.client.get("/api/v1/scheduling/seasons")
        data = response.json()
        self.assertEqual(data[0]["name"], "2024-2025 Season")
        self.assertEqual(data[1]["name"], "2023-2024 Season")

    def test_get_season(self):
        """Test GET /api/v1/scheduling/seasons/{public_id} returns season details."""
        response = self.client.get(
            f"/api/v1/scheduling/seasons/{self.season1.public_id}"
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["name"], "2024-2025 Season")
        self.assertEqual(data["start_date"], "2024-09-01")
        self.assertEqual(data["end_date"], "2025-06-30")

    def test_get_season_not_found(self):
        """Test GET with non-existent public_id returns 404."""
        response = self.client.get("/api/v1/scheduling/seasons/nonexistent123")
        self.assertEqual(response.status_code, 404)

    def test_create_season(self):
        """Test POST /api/v1/scheduling/seasons creates a season."""
        payload = {
            "name": "2025-2026 Season",
            "start_date": "2025-09-01",
            "end_date": "2026-06-30",
        }
        response = self.client.post(
            "/api/v1/scheduling/seasons",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["name"], "2025-2026 Season")
        self.assertIn("public_id", data)

    def test_create_season_missing_required_field(self):
        """Test POST with missing required field returns 422."""
        payload = {
            "name": "2025-2026 Season",
            "start_date": "2025-09-01",
            # missing end_date
        }
        response = self.client.post(
            "/api/v1/scheduling/seasons",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 422)

    def test_update_season_put(self):
        """Test PUT /api/v1/scheduling/seasons/{public_id} fully updates season."""
        payload = {
            "name": "Updated Season",
            "start_date": "2024-08-01",
            "end_date": "2025-07-31",
        }
        response = self.client.put(
            f"/api/v1/scheduling/seasons/{self.season1.public_id}",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["name"], "Updated Season")
        self.assertEqual(data["start_date"], "2024-08-01")

    def test_partial_update_season_patch(self):
        """Test PATCH /api/v1/scheduling/seasons/{public_id} partially updates season."""  # noqa: E501
        payload = {"name": "Partially Updated Season"}
        response = self.client.patch(
            f"/api/v1/scheduling/seasons/{self.season1.public_id}",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["name"], "Partially Updated Season")
        self.assertEqual(data["start_date"], "2024-09-01")  # Unchanged

    def test_delete_season(self):
        """Test DELETE /api/v1/scheduling/seasons/{public_id} removes season."""
        response = self.client.delete(
            f"/api/v1/scheduling/seasons/{self.season1.public_id}"
        )
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Season.objects.filter(pk=self.season1.pk).exists())

    def test_delete_season_not_found(self):
        """Test DELETE with non-existent public_id returns 404."""
        response = self.client.delete("/api/v1/scheduling/seasons/nonexistent123")
        self.assertEqual(response.status_code, 404)
