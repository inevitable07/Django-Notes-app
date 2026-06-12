"""
Business-logic layer for notes.

Keeps views thin by isolating data-access and business rules here.
All database queries and mutations go through this module.
"""

from django.shortcuts import get_object_or_404

from .models import Note
from .serializers import NoteSerializer


def get_all_notes(user_clerk_id: str) -> list[dict]:
    """Return all notes for the authenticated user ordered by latest first."""
    notes = Note.objects.filter(user_clerk_id=user_clerk_id)
    serializer = NoteSerializer(notes, many=True)
    return serializer.data


def create_note(data: dict, user_clerk_id: str) -> tuple[dict | None, dict | None]:
    """
    Validate and persist a new note for the authenticated user.

    Returns:
        (serialized_data, None) on success.
        (None, errors_dict) on validation failure.
    """
    data_with_user = {**data, "user_clerk_id": user_clerk_id}
    serializer = NoteSerializer(data=data_with_user)
    if serializer.is_valid():
        serializer.save()
        return serializer.data, None
    return None, serializer.errors


def delete_note(note_id: int, user_clerk_id: str) -> None:
    """
    Delete a note by its primary key if it belongs to the authenticated user.

    Raises Http404 if the note does not exist or doesn't belong to the user.
    """
    note = get_object_or_404(Note, pk=note_id, user_clerk_id=user_clerk_id)
    note.delete()
