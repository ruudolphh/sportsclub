# people/schemas/common.py
from ninja import Schema


class PersonRef(Schema):
    """Reference to a person, for embedding in related resources."""

    public_id: str
    display_name: str

    @staticmethod
    def resolve_display_name(obj):
        """Generate display name from the model's __str__ method."""
        return str(obj)
