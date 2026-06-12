"""
Note model — the single source of truth for the database schema.
"""

from django.db import models


class Note(models.Model):
    """Represents a single note created by a user."""

    user_clerk_id = models.CharField(max_length=255, db_index=True)
    title = models.CharField(max_length=100)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]  # Latest notes first
        verbose_name = "Note"
        verbose_name_plural = "Notes"
        indexes = [models.Index(fields=["user_clerk_id", "-created_at"])]

    def __str__(self) -> str:
        return self.title
