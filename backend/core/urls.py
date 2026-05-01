"""
Root URL configuration for the Notes API.

All API routes are namespaced under /api/.
"""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("notes.urls")),
]
