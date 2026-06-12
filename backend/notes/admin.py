from django.contrib import admin

from .models import Note


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    """Admin interface for Note model."""

    list_display = ("id", "user_clerk_id", "title", "created_at")
    list_filter = ("user_clerk_id", "created_at")
    search_fields = ("title", "content", "user_clerk_id")
    ordering = ("-created_at",)
    readonly_fields = ("user_clerk_id", "created_at", "id")
