from django.contrib import admin

from .models import Note


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    """Admin interface for Note model."""

    list_display = ("id", "title", "created_at")
    list_filter = ("created_at",)
    search_fields = ("title", "content")
    ordering = ("-created_at",)
