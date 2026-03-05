# core/schemas.py
from ninja import Field, Schema
from pydantic import ConfigDict, field_validator


class AddressIn(Schema):
    """Schema for creating/updating an address."""

    # Django Ninja automatically reads `json_schema_extra` and includes the examples
    # in the generated Open API docs.
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "line1": "Av. de Jaume III, 15",
                    "line2": "Centre",
                    "postal_code": "07012",
                    "city": "Palma",
                    "state": "Illes Balears",
                    "country": "Spain",
                }
            ]
        }
    )

    line1: str = Field(
        ..., min_length=1, max_length=255, description="Primary address information"
    )
    line2: str = Field(
        "",
        max_length=255,
        description="Secondary address information",
    )
    postal_code: str = Field("", max_length=20, description="Postal code")
    city: str = Field("", max_length=100, description="City name")
    state: str = Field("", max_length=100, description="State, province or region")
    country: str = Field("", max_length=100, description="Country name")

    @field_validator("postal_code")
    @classmethod
    def validate_postal_code(cls, v):
        """Remove whitespace for consistency."""
        if v:
            v = v.strip()
        return v


class AddressOut(Schema):
    """Schema for returning address data."""

    public_id: str
    line1: str
    line2: str
    postal_code: str
    city: str
    state: str
    country: str
    formatted_address: str

    @staticmethod
    def resolve_formatted_address(obj):
        """Generate formatted address from the model's __str__ method."""
        return str(obj)


class AddressListOut(Schema):
    """Simplified schema for listing addresses."""

    public_id: str
    formatted_address: str

    @staticmethod
    def resolve_formatted_address(obj):
        """Generate formatted address from the model's __str__ method."""
        return str(obj)


class AddressPatch(Schema):
    """Schema for partially updating an address (PATCH). All fields optional."""

    line1: str | None = Field(None, min_length=1, max_length=255)
    line2: str | None = Field(None, max_length=255)
    postal_code: str | None = Field(None, max_length=20)
    city: str | None = Field(None, max_length=100)
    state: str | None = Field(None, max_length=100)
    country: str | None = Field(None, max_length=100)


class ErrorResponse(Schema):
    """Standard error response."""

    detail: str


class ValidationErrorResponse(Schema):
    """Validation error response with field-level details."""

    detail: dict[str, list[str]]
