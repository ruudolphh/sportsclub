# sportsclub/tests/test_acceptance_workflows.py
"""
Acceptance tests for cross-app workflows.

These tests verify complete user journeys that span multiple apps,
ensuring the API works correctly as an integrated system.
"""

import json

from django.test import TestCase


class CompetitionWorkflowTest(TestCase):
    """Test complete workflow for setting up and managing a competition."""

    def test_full_competition_setup_workflow(self):
        """
        Test the complete workflow of setting up a competition:
        1. Create an address
        2. Create a venue at that address
        3. Create a season
        4. Create a coach
        5. Create athletes
        6. Create a competition with all the above
        7. Verify all relationships are correct
        """
        # Step 1: Create an address
        address_payload = {
            "line1": "Carrer dels Esports, 1",
            "city": "Palma",
            "postal_code": "07001",
            "country": "Spain",
        }
        response = self.client.post(
            "/api/v1/core/addresses",
            data=json.dumps(address_payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        address = response.json()
        address_public_id = address["public_id"]

        # Step 2: Create a venue at that address
        venue_payload = {
            "name": "Estadi Balear",
            "address_public_id": address_public_id,
        }
        response = self.client.post(
            "/api/v1/inventory/venues",
            data=json.dumps(venue_payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        venue = response.json()
        venue_public_id = venue["public_id"]
        self.assertEqual(venue["address"]["city"], "Palma")

        # Step 3: Create a season
        season_payload = {
            "name": "Temporada 2024-2025",
            "start_date": "2024-09-01",
            "end_date": "2025-06-30",
        }
        response = self.client.post(
            "/api/v1/scheduling/seasons",
            data=json.dumps(season_payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        season = response.json()
        season_public_id = season["public_id"]

        # Step 4: Create a coach
        coach_payload = {
            "first_name": "Maria",
            "last_name": "Garcia",
            "email": "maria.garcia@example.com",
            "date_of_birth": "1980-05-15",
            "certification": "entrenador_nacional",
        }
        response = self.client.post(
            "/api/v1/people/coaches",
            data=json.dumps(coach_payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        coach = response.json()
        coach_public_id = coach["public_id"]

        # Step 5: Create athletes
        athlete_public_ids = []
        for i, (first, last) in enumerate(
            [("Ana", "Martinez"), ("Carlos", "Lopez"), ("Elena", "Sanchez")]
        ):
            athlete_payload = {
                "first_name": first,
                "last_name": last,
                "email": f"{first.lower()}.{last.lower()}@example.com",
                "date_of_birth": f"200{i}-01-15",
                "jersey_number": 10 + i,
            }
            response = self.client.post(
                "/api/v1/people/athletes",
                data=json.dumps(athlete_payload),
                content_type="application/json",
            )
            self.assertEqual(response.status_code, 201)
            athlete_public_ids.append(response.json()["public_id"])

        # Step 6: Create competition with all relationships
        competition_payload = {
            "name": "Campionat de Balears",
            "date": "2025-04-15T10:00:00Z",
            "venue_public_id": venue_public_id,
            "season_public_id": season_public_id,
            "coach_public_ids": [coach_public_id],
            "athlete_public_ids": athlete_public_ids,
        }
        response = self.client.post(
            "/api/v1/scheduling/competitions",
            data=json.dumps(competition_payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        competition = response.json()

        # Step 7: Verify all relationships
        self.assertEqual(competition["name"], "Campionat de Balears")
        self.assertEqual(competition["venue"]["name"], "Estadi Balear")
        self.assertEqual(competition["season"]["name"], "Temporada 2024-2025")
        self.assertEqual(len(competition["coaches"]), 1)
        self.assertEqual(competition["coaches"][0]["display_name"], "Maria Garcia")
        self.assertEqual(len(competition["athletes"]), 3)

    def test_training_schedule_workflow(self):
        """
        Test the workflow for scheduling training sessions:
        1. Create necessary resources (season, coach, athletes)
        2. Create multiple training sessions
        3. Verify trainings are listed correctly
        """
        # Create a season
        season_payload = {
            "name": "Pre-Season 2025",
            "start_date": "2025-07-01",
            "end_date": "2025-08-31",
        }
        response = self.client.post(
            "/api/v1/scheduling/seasons",
            data=json.dumps(season_payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        season_public_id = response.json()["public_id"]

        # Create a coach
        coach_payload = {
            "first_name": "Pedro",
            "last_name": "Fernandez",
            "email": "pedro.fernandez@example.com",
        }
        response = self.client.post(
            "/api/v1/people/coaches",
            data=json.dumps(coach_payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        coach_public_id = response.json()["public_id"]

        # Create training sessions with different focuses
        training_focuses = [
            ("Sprint Training", "Explosive starts and acceleration"),
            ("Endurance Training", "Long distance running"),
            ("Technical Training", "Hurdle technique"),
        ]

        for i, (name, focus) in enumerate(training_focuses):
            training_payload = {
                "name": name,
                "date": f"2025-07-{10 + i}T09:00:00Z",
                "season_public_id": season_public_id,
                "coach_public_ids": [coach_public_id],
                "focus": focus,
            }
            response = self.client.post(
                "/api/v1/scheduling/trainings",
                data=json.dumps(training_payload),
                content_type="application/json",
            )
            self.assertEqual(response.status_code, 201)

        # Verify all trainings are listed
        response = self.client.get("/api/v1/scheduling/trainings")
        self.assertEqual(response.status_code, 200)
        trainings = response.json()
        self.assertEqual(len(trainings), 3)


class AthleteManagementWorkflowTest(TestCase):
    """Test workflows for managing athletes and their relationships."""

    def test_athlete_with_address_workflow(self):
        """
        Test creating an athlete with a home address:
        1. Create an address
        2. Create an athlete linked to the address
        3. Update the athlete's address
        4. Remove the athlete's address
        """
        # Create address
        address_payload = {
            "line1": "Carrer Major, 10",
            "city": "Inca",
            "postal_code": "07300",
            "country": "Spain",
        }
        response = self.client.post(
            "/api/v1/core/addresses",
            data=json.dumps(address_payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        address1_public_id = response.json()["public_id"]

        # Create athlete with address
        athlete_payload = {
            "first_name": "Miguel",
            "last_name": "Torres",
            "email": "miguel.torres@example.com",
            "address_public_id": address1_public_id,
        }
        response = self.client.post(
            "/api/v1/people/athletes",
            data=json.dumps(athlete_payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        athlete = response.json()
        athlete_public_id = athlete["public_id"]
        self.assertEqual(athlete["address"]["city"], "Inca")

        # Create a new address
        address2_payload = {
            "line1": "Avinguda del Parc, 5",
            "city": "Manacor",
            "postal_code": "07500",
            "country": "Spain",
        }
        response = self.client.post(
            "/api/v1/core/addresses",
            data=json.dumps(address2_payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        address2_public_id = response.json()["public_id"]

        # Update athlete's address using PATCH
        patch_payload = {"address_public_id": address2_public_id}
        response = self.client.patch(
            f"/api/v1/people/athletes/{athlete_public_id}",
            data=json.dumps(patch_payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["address"]["city"], "Manacor")

        # Remove athlete's address
        patch_payload = {"address_public_id": None}
        response = self.client.patch(
            f"/api/v1/people/athletes/{athlete_public_id}",
            data=json.dumps(patch_payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.json()["address"])

    def test_delete_address_sets_athlete_address_null(self):
        """Test that deleting an address sets athlete's address to null (SET_NULL)."""
        # Create address
        address_payload = {"line1": "Test Street", "city": "Palma"}
        response = self.client.post(
            "/api/v1/core/addresses",
            data=json.dumps(address_payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        address_public_id = response.json()["public_id"]

        # Create athlete with address
        athlete_payload = {
            "first_name": "Test",
            "last_name": "Athlete",
            "email": "test.athlete@example.com",
            "address_public_id": address_public_id,
        }
        response = self.client.post(
            "/api/v1/people/athletes",
            data=json.dumps(athlete_payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        athlete_public_id = response.json()["public_id"]
        self.assertIsNotNone(response.json()["address"])

        # Delete the address
        response = self.client.delete(f"/api/v1/core/addresses/{address_public_id}")
        self.assertEqual(response.status_code, 204)

        # Verify athlete's address is now null
        response = self.client.get(f"/api/v1/people/athletes/{athlete_public_id}")
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.json()["address"])


class CompetitionScoreWorkflowTest(TestCase):
    """Test workflows for managing competition scores."""

    def test_add_and_update_competition_score(self):
        """
        Test adding and updating scores to a competition:
        1. Create a competition without score
        2. Add score via PATCH
        3. Update score with more results
        """
        # Create season first
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

        # Create competition without score
        competition_payload = {
            "name": "Regional Championship",
            "date": "2025-05-01T10:00:00Z",
            "season_public_id": season_public_id,
        }
        response = self.client.post(
            "/api/v1/scheduling/competitions",
            data=json.dumps(competition_payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        competition = response.json()
        competition_public_id = competition["public_id"]
        self.assertIsNone(competition["score"])

        # Add score via PATCH
        score_payload = {
            "score": {"results": {"sprints": {"gold": 2, "silver": 1, "bronze": 3}}}
        }
        response = self.client.patch(
            f"/api/v1/scheduling/competitions/{competition_public_id}",
            data=json.dumps(score_payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        competition = response.json()
        self.assertIsNotNone(competition["score"])
        self.assertEqual(competition["score"]["results"]["sprints"]["gold"], 2)

        # Update score with additional results
        score_payload = {
            "score": {
                "results": {
                    "sprints": {"gold": 2, "silver": 1, "bronze": 3},
                    "high_jump": {"gold": 1, "silver": 2, "bronze": 0},
                }
            }
        }
        response = self.client.patch(
            f"/api/v1/scheduling/competitions/{competition_public_id}",
            data=json.dumps(score_payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        competition = response.json()
        self.assertIn("high_jump", competition["score"]["results"])


class SeasonCascadeWorkflowTest(TestCase):
    """Test cascade behavior when deleting seasons."""

    def test_delete_season_cascades_to_activities(self):
        """
        Test that deleting a season also deletes its competitions and trainings.
        """
        # Create season
        season_payload = {
            "name": "Temporary Season",
            "start_date": "2025-01-01",
            "end_date": "2025-06-30",
        }
        response = self.client.post(
            "/api/v1/scheduling/seasons",
            data=json.dumps(season_payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        season_public_id = response.json()["public_id"]

        # Create a competition in this season
        competition_payload = {
            "name": "Test Competition",
            "date": "2025-03-01T10:00:00Z",
            "season_public_id": season_public_id,
        }
        response = self.client.post(
            "/api/v1/scheduling/competitions",
            data=json.dumps(competition_payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        competition_public_id = response.json()["public_id"]

        # Create a training in this season
        training_payload = {
            "name": "Test Training",
            "date": "2025-02-15T09:00:00Z",
            "season_public_id": season_public_id,
            "focus": "General fitness",
        }
        response = self.client.post(
            "/api/v1/scheduling/trainings",
            data=json.dumps(training_payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        training_public_id = response.json()["public_id"]

        # Verify both exist
        response = self.client.get(
            f"/api/v1/scheduling/competitions/{competition_public_id}"
        )
        self.assertEqual(response.status_code, 200)
        response = self.client.get(f"/api/v1/scheduling/trainings/{training_public_id}")
        self.assertEqual(response.status_code, 200)

        # Delete the season
        response = self.client.delete(f"/api/v1/scheduling/seasons/{season_public_id}")
        self.assertEqual(response.status_code, 204)

        # Verify competition and training are also deleted (cascade)
        response = self.client.get(
            f"/api/v1/scheduling/competitions/{competition_public_id}"
        )
        self.assertEqual(response.status_code, 404)
        response = self.client.get(f"/api/v1/scheduling/trainings/{training_public_id}")
        self.assertEqual(response.status_code, 404)
