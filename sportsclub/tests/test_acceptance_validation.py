# sportsclub/tests/test_acceptance_validation.py
"""
Acceptance tests for data validation across the API.

These tests verify that the API properly validates input data
and returns appropriate error responses.
"""

import json

from django.test import TestCase


class AddressValidationTest(TestCase):
    """Test validation for Address endpoints."""

    def test_address_requires_line1(self):
        """Test that address creation requires line1."""
        payload = {"city": "Palma", "country": "Spain"}
        response = self.client.post(
            "/api/v1/core/addresses",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 422)

    def test_address_line1_cannot_be_empty(self):
        """Test that line1 cannot be an empty string."""
        payload = {"line1": ""}
        response = self.client.post(
            "/api/v1/core/addresses",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 422)


class AthleteValidationTest(TestCase):
    """Test validation for Athlete endpoints."""

    def test_athlete_requires_email(self):
        """Test that athlete creation requires email."""
        payload = {"first_name": "Test", "last_name": "Athlete"}
        response = self.client.post(
            "/api/v1/people/athletes",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 422)

    def test_athlete_email_must_be_valid(self):
        """Test that athlete email must be valid format."""
        payload = {
            "first_name": "Test",
            "last_name": "Athlete",
            "email": "not-an-email",
        }
        response = self.client.post(
            "/api/v1/people/athletes",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 422)

    def test_athlete_height_must_be_positive(self):
        """Test that athlete height must be positive."""
        payload = {
            "first_name": "Test",
            "last_name": "Athlete",
            "email": "test@example.com",
            "height": -175.0,
        }
        response = self.client.post(
            "/api/v1/people/athletes",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 422)

    def test_athlete_weight_must_be_positive(self):
        """Test that athlete weight must be positive."""
        payload = {
            "first_name": "Test",
            "last_name": "Athlete",
            "email": "test@example.com",
            "weight": 0,
        }
        response = self.client.post(
            "/api/v1/people/athletes",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 422)

    def test_athlete_invalid_address_returns_404(self):
        """Test that invalid address_public_id returns 404."""
        payload = {
            "first_name": "Test",
            "last_name": "Athlete",
            "email": "test@example.com",
            "address_public_id": "nonexistent123",
        }
        response = self.client.post(
            "/api/v1/people/athletes",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 404)


class CoachValidationTest(TestCase):
    """Test validation for Coach endpoints."""

    def test_coach_invalid_certification_rejected(self):
        """Test that invalid certification value is rejected."""
        payload = {
            "first_name": "Test",
            "last_name": "Coach",
            "email": "test.coach@example.com",
            "certification": "INVALID_CERT",
        }
        response = self.client.post(
            "/api/v1/people/coaches",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 422)

    def test_coach_valid_certification_accepted(self):
        """Test that valid certification values are accepted."""
        valid_certifications = [
            "tecnico_deportivo_grado_medio",
            "tecnico_deportivo_grado_superior",
            "entrenador_nacional",
            "entrenador_club",
            "nsca_cpt",
        ]
        for i, cert in enumerate(valid_certifications):
            payload = {
                "first_name": f"Coach{i}",
                "last_name": "Test",
                "email": f"coach{i}@example.com",
                "certification": cert,
            }
            response = self.client.post(
                "/api/v1/people/coaches",
                data=json.dumps(payload),
                content_type="application/json",
            )
            self.assertEqual(
                response.status_code, 201, f"Certification {cert} should be valid"
            )


class SeasonValidationTest(TestCase):
    """Test validation for Season endpoints."""

    def test_season_requires_all_fields(self):
        """Test that season requires name, start_date, and end_date."""
        # Missing end_date
        payload = {"name": "Test Season", "start_date": "2025-01-01"}
        response = self.client.post(
            "/api/v1/scheduling/seasons",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 422)

        # Missing start_date
        payload = {"name": "Test Season", "end_date": "2025-12-31"}
        response = self.client.post(
            "/api/v1/scheduling/seasons",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 422)

        # Missing name
        payload = {"start_date": "2025-01-01", "end_date": "2025-12-31"}
        response = self.client.post(
            "/api/v1/scheduling/seasons",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 422)


class CompetitionValidationTest(TestCase):
    """Test validation for Competition endpoints."""

    def test_competition_requires_season(self):
        """Test that competition requires season_public_id."""
        payload = {
            "name": "Test Competition",
            "date": "2025-05-01T10:00:00Z",
        }
        response = self.client.post(
            "/api/v1/scheduling/competitions",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 422)

    def test_competition_invalid_season_returns_404(self):
        """Test that invalid season_public_id returns 404."""
        payload = {
            "name": "Test Competition",
            "date": "2025-05-01T10:00:00Z",
            "season_public_id": "nonexistent123",
        }
        response = self.client.post(
            "/api/v1/scheduling/competitions",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 404)

    def test_competition_invalid_score_discipline_rejected(self):
        """Test that invalid discipline in score is rejected."""
        # First create a valid season
        season_payload = {
            "name": "Test Season",
            "start_date": "2025-01-01",
            "end_date": "2025-12-31",
        }
        response = self.client.post(
            "/api/v1/scheduling/seasons",
            data=json.dumps(season_payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        season_public_id = response.json()["public_id"]

        # Try to create competition with invalid discipline
        payload = {
            "name": "Test Competition",
            "date": "2025-05-01T10:00:00Z",
            "season_public_id": season_public_id,
            "score": {
                "results": {"invalid_discipline": {"gold": 1, "silver": 0, "bronze": 0}}
            },
        }
        response = self.client.post(
            "/api/v1/scheduling/competitions",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 422)


class NotFoundValidationTest(TestCase):
    """Test 404 responses for non-existent resources."""

    def test_get_nonexistent_address_returns_404(self):
        """Test GET for non-existent address returns 404."""
        response = self.client.get("/api/v1/core/addresses/nonexistent123")
        self.assertEqual(response.status_code, 404)

    def test_get_nonexistent_athlete_returns_404(self):
        """Test GET for non-existent athlete returns 404."""
        response = self.client.get("/api/v1/people/athletes/nonexistent123")
        self.assertEqual(response.status_code, 404)

    def test_get_nonexistent_coach_returns_404(self):
        """Test GET for non-existent coach returns 404."""
        response = self.client.get("/api/v1/people/coaches/nonexistent123")
        self.assertEqual(response.status_code, 404)

    def test_get_nonexistent_venue_returns_404(self):
        """Test GET for non-existent venue returns 404."""
        response = self.client.get("/api/v1/inventory/venues/nonexistent123")
        self.assertEqual(response.status_code, 404)

    def test_get_nonexistent_season_returns_404(self):
        """Test GET for non-existent season returns 404."""
        response = self.client.get("/api/v1/scheduling/seasons/nonexistent123")
        self.assertEqual(response.status_code, 404)

    def test_get_nonexistent_competition_returns_404(self):
        """Test GET for non-existent competition returns 404."""
        response = self.client.get("/api/v1/scheduling/competitions/nonexistent123")
        self.assertEqual(response.status_code, 404)

    def test_get_nonexistent_training_returns_404(self):
        """Test GET for non-existent training returns 404."""
        response = self.client.get("/api/v1/scheduling/trainings/nonexistent123")
        self.assertEqual(response.status_code, 404)
