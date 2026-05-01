"""
URL routes for the notes app.

Mounted at /api/ by the project-level urls.py.
"""

from django.urls import path

from . import views

urlpatterns = [
    path("notes/", views.notes_list_create, name="notes-list-create"),
    path("notes/<int:pk>/", views.notes_delete, name="notes-delete"),
]
