"""
Serializers for the Note model.

Handles validation, transformation between Python objects and JSON,
and enforcing field constraints beyond what the model provides.
"""

from rest_framework import serializers

from .models import Note


class NoteSerializer(serializers.ModelSerializer):
    """Serialize / deserialize Note instances."""

    class Meta:
        model = Note
        fields = ["id", "user_clerk_id", "title", "content", "created_at"]
        read_only_fields = ["id", "user_clerk_id", "created_at"]

    # ── Extra validation ──────────────────────────────

    def validate_title(self, value: str) -> str:
        """Reject blank or whitespace-only titles."""
        cleaned = value.strip()
        if not cleaned:
            raise serializers.ValidationError("Title cannot be blank.")
        return cleaned

    def validate_content(self, value: str) -> str:
        """Reject blank or whitespace-only content."""
        cleaned = value.strip()
        if not cleaned:
            raise serializers.ValidationError("Content cannot be blank.")
        return cleaned
