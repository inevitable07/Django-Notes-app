"""
Business-logic layer for notes.

Keeps views thin by isolating data-access and business rules here.
All database queries and mutations go through this module.
"""

from django.shortcuts import get_object_or_404

from .models import Note
from .serializers import NoteSerializer


def get_all_notes() -> list[dict]:
    """Return all notes ordered by latest first (default model ordering)."""
    notes = Note.objects.all()
    serializer = NoteSerializer(notes, many=True)
    return serializer.data


def create_note(data: dict) -> tuple[dict | None, dict | None]:
    """
    Validate and persist a new note.

    Returns:
        (serialized_data, None) on success.
        (None, errors_dict) on validation failure.
    """
    serializer = NoteSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return serializer.data, None
    return None, serializer.errors


def delete_note(note_id: int) -> None:
    """
    Delete a note by its primary key.

    Raises Http404 if the note does not exist.
    """
    note = get_object_or_404(Note, pk=note_id)
    note.delete()
