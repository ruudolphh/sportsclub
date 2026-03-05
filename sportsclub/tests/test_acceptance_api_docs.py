# tests/test_acceptance_api_docs.py
"""Acceptance tests for API documentation and schema."""

from django.test import TestCase


class OpenAPISchemaTest(TestCase):
    """Test that OpenAPI documentation is accessible and complete."""

    def test_openapi_schema_accessible(self):
        """Test that OpenAPI JSON schema is accessible."""
        response = self.client.get("/api/v1/openapi.json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")

    def test_openapi_schema_has_info(self):
        """Test that OpenAPI schema contains required info fields."""
        response = self.client.get("/api/v1/openapi.json")
        data = response.json()

        self.assertIn("info", data)
        self.assertIn("title", data["info"])
        self.assertIn("version", data["info"])

        # Verify they're non-empty strings
        self.assertIsInstance(data["info"]["title"], str)
        self.assertIsInstance(data["info"]["version"], str)
        self.assertGreater(len(data["info"]["title"]), 0)
        self.assertGreater(len(data["info"]["version"]), 0)

    def test_openapi_schema_has_paths(self):
        """Test that OpenAPI schema contains all expected paths."""
        response = self.client.get("/api/v1/openapi.json")
        data = response.json()
        paths = data.get("paths", {})

        # Core app
        self.assertIn("/api/v1/core/addresses", paths)

        # Inventory app
        self.assertIn("/api/v1/inventory/venues", paths)

        # People app
        self.assertIn("/api/v1/people/athletes", paths)
        self.assertIn("/api/v1/people/coaches", paths)

        # Scheduling app
        self.assertIn("/api/v1/scheduling/seasons", paths)
        self.assertIn("/api/v1/scheduling/competitions", paths)
        self.assertIn("/api/v1/scheduling/trainings", paths)

    def test_openapi_schema_has_required_http_methods(self):
        """Test that endpoints have expected HTTP methods."""
        response = self.client.get("/api/v1/openapi.json")
        data = response.json()
        paths = data.get("paths", {})

        # Check that collection endpoints have GET and POST
        collection_endpoints = [
            "/api/v1/core/addresses",
            "/api/v1/inventory/venues",
            "/api/v1/people/athletes",
            "/api/v1/people/coaches",
            "/api/v1/scheduling/seasons",
            "/api/v1/scheduling/competitions",
            "/api/v1/scheduling/trainings",
        ]
        for endpoint in collection_endpoints:
            self.assertIn("get", paths[endpoint], f"{endpoint} missing GET")
            self.assertIn("post", paths[endpoint], f"{endpoint} missing POST")

    def test_openapi_schema_version_format(self):
        """Test that API version follows semantic versioning pattern."""

        response = self.client.get("/api/v1/openapi.json")
        data = response.json()
        version = data["info"]["version"]

        # Semantic versioning pattern: MAJOR.MINOR.PATCH (PATCH optional)
        semver_pattern = r"^\d+\.\d+(\.\d+)?$"
        self.assertRegex(
            version,
            semver_pattern,
            f"Version '{version}' doesn't follow semantic versioning",
        )

    def test_swagger_ui_accessible(self):
        """Test that Swagger UI documentation page is accessible."""
        response = self.client.get("/api/v1/docs")
        self.assertEqual(response.status_code, 200)

    def test_openapi_schema_includes_components(self):
        """Test that OpenAPI schema includes component schemas."""
        response = self.client.get("/api/v1/openapi.json")
        data = response.json()
        components = data.get("components", {}).get("schemas", {})

        # Verify schemas exist (check that there are some schemas defined)
        self.assertGreater(len(components), 0, "No component schemas found")

        # Verify key schemas exist by checking for partial matches
        schema_names = list(components.keys())
        schema_names_lower = [name.lower() for name in schema_names]

        expected_patterns = [
            "address",
            "athlete",
            "coach",
            "venue",
            "season",
            "competition",
            "training",
        ]
        for pattern in expected_patterns:
            self.assertTrue(
                any(pattern in name for name in schema_names_lower),
                f"No schema containing '{pattern}' found in components",
            )
