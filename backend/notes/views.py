"""
API views for notes.

Uses DRF's @api_view decorator for a clean, function-based approach.
All heavy lifting is delegated to the services layer.
"""

import logging

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from . import services

logger = logging.getLogger(__name__)


@api_view(["GET", "POST"])
def notes_list_create(request: Request) -> Response:
    """
    GET  /api/notes/  → List all notes (latest first).
    POST /api/notes/  → Create a new note.
    """
    if request.method == "GET":
        try:
            data = services.get_all_notes()
            return Response(data, status=status.HTTP_200_OK)
        except Exception:
            logger.exception("Failed to fetch notes")
            return Response(
                {"error": "Unable to fetch notes. Please try again later."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    # POST
    try:
        note_data, errors = services.create_note(request.data)
        if errors:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(note_data, status=status.HTTP_201_CREATED)
    except Exception:
        logger.exception("Failed to create note")
        return Response(
            {"error": "Unable to create note. Please try again later."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["DELETE"])
def notes_delete(request: Request, pk: int) -> Response:
    """
    DELETE /api/notes/{id}/ → Delete a note by primary key.
    """
    try:
        services.delete_note(pk)
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Exception as exc:
        # get_object_or_404 raises Http404 which DRF handles automatically
        # before this point, so if we land here it's a genuine server error.
        if "Http404" in type(exc).__name__ or "404" in str(exc):
            raise  # Let DRF's exception handler return 404
        logger.exception("Failed to delete note %s", pk)
        return Response(
            {"error": "Unable to delete note. Please try again later."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
