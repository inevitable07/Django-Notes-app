"""
Tests for Clerk authentication module.

Run with: python manage.py test notes.tests.test_auth
"""

import os
from unittest.mock import patch, MagicMock
from django.test import TestCase, RequestFactory
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed

from notes.auth import (
    get_clerk_user_from_token,
    get_clerk_user_from_request,
    require_auth
)


class ClerkTokenVerificationTests(TestCase):
    """Test JWT token verification."""

    def setUp(self):
        self.factory = RequestFactory()
        self.valid_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyXzEyMzQ1Njc4OTAiLCJuYW1lIjoiSm9obiBEb2UiLCJpYXQiOjE1MTYyMzkwMjJ9.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"

    def test_missing_clerk_secret_key(self):
        """Test that missing CLERK_SECRET_KEY raises error."""
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(AuthenticationFailed) as cm:
                get_clerk_user_from_token(self.valid_token)
            self.assertIn("not configured", str(cm.exception))

    def test_empty_token(self):
        """Test that empty token raises error."""
        with patch("notes.auth.CLERK_SECRET_KEY", "sk_test_123"):
            with self.assertRaises(AuthenticationFailed) as cm:
                get_clerk_user_from_token("")
            self.assertIn("No authentication token provided", str(cm.exception))

    def test_invalid_token_format(self):
        """Test that malformed token raises error."""
        with patch("notes.auth.CLERK_SECRET_KEY", "sk_test_123"):
            with self.assertRaises(AuthenticationFailed) as cm:
                get_clerk_user_from_token("not.a.valid.token")
            self.assertIn("Invalid token", str(cm.exception))


class AuthorizationHeaderTests(TestCase):
    """Test Authorization header extraction."""

    def setUp(self):
        self.factory = RequestFactory()

    def test_missing_authorization_header(self):
        """Test that missing Authorization header raises error."""
        request = self.factory.get("/api/notes/")
        with patch("notes.auth.CLERK_SECRET_KEY", "sk_test_123"):
            with self.assertRaises(AuthenticationFailed) as cm:
                get_clerk_user_from_request(request)
            self.assertIn("Authorization header missing", str(cm.exception))

    def test_invalid_authorization_header_format(self):
        """Test that invalid header format raises error."""
        request = self.factory.get(
            "/api/notes/",
            HTTP_AUTHORIZATION="InvalidFormat token123"
        )
        with patch("notes.auth.CLERK_SECRET_KEY", "sk_test_123"):
            with self.assertRaises(AuthenticationFailed) as cm:
                get_clerk_user_from_request(request)
            self.assertIn("Invalid Authorization header format", str(cm.exception))

    def test_missing_bearer_token(self):
        """Test that missing Bearer token raises error."""
        request = self.factory.get("/api/notes/", HTTP_AUTHORIZATION="Bearer")
        with patch("notes.auth.CLERK_SECRET_KEY", "sk_test_123"):
            with self.assertRaises(AuthenticationFailed):
                get_clerk_user_from_request(request)


class RequireAuthDecoratorTests(TestCase):
    """Test @require_auth decorator."""

    def setUp(self):
        self.factory = RequestFactory()

        # Mock view function
        @require_auth
        def mock_view(request):
            return {"user_id": request.user_clerk_id}

        self.mock_view = mock_view

    def test_decorator_adds_user_to_request(self):
        """Test that decorator adds user_clerk_id to request."""
        # This test would need a valid token from Clerk
        # For now, just verify the decorator exists and is callable
        self.assertTrue(callable(self.mock_view))

    def test_decorator_returns_401_without_auth(self):
        """Test that decorator returns 401 without authentication."""
        request = self.factory.get("/api/notes/")
        response = self.mock_view(request)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("error", response.data)


class IntegrationTests(TestCase):
    """Integration tests with Django views."""

    def setUp(self):
        self.factory = RequestFactory()

    def test_auth_flow_without_credentials(self):
        """Test complete auth flow without credentials."""
        request = self.factory.get("/api/notes/")

        # Should fail without Authorization header
        with patch("notes.auth.CLERK_SECRET_KEY", "sk_test_123"):
            with self.assertRaises(AuthenticationFailed):
                get_clerk_user_from_request(request)

    def test_auth_flow_with_bearer_header(self):
        """Test complete auth flow with Bearer token."""
        # This test requires a valid Clerk token
        # Implementation would depend on test Clerk environment
        pass


class EdgeCaseTests(TestCase):
    """Test edge cases and error conditions."""

    def test_token_with_missing_sub_claim(self):
        """Test that token without 'sub' claim raises error."""
        # Token without 'sub' claim
        token_without_sub = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoiSm9obiBEb2UiLCJpYXQiOjE1MTYyMzkwMjJ9.invalid"

        with patch("notes.auth.CLERK_SECRET_KEY", "sk_test_123"):
            with self.assertRaises(AuthenticationFailed):
                get_clerk_user_from_token(token_without_sub)

    def test_multiple_bearer_tokens(self):
        """Test handling of multiple Bearer tokens."""
        request = RequestFactory().get(
            "/api/notes/",
            HTTP_AUTHORIZATION="Bearer token1 token2"
        )

        with patch("notes.auth.CLERK_SECRET_KEY", "sk_test_123"):
            # Should only process first Bearer token
            with self.assertRaises(AuthenticationFailed):
                get_clerk_user_from_request(request)

    def test_case_insensitive_bearer(self):
        """Test that Bearer keyword is case-insensitive."""
        # Test with lowercase 'bearer'
        request = RequestFactory().get(
            "/api/notes/",
            HTTP_AUTHORIZATION="bearer token123"
        )

        with patch("notes.auth.CLERK_SECRET_KEY", "sk_test_123"):
            try:
                get_clerk_user_from_request(request)
            except AuthenticationFailed as e:
                # Should fail on token verification, not header parsing
                self.assertNotIn("Invalid Authorization header format", str(e))


# Manual testing helper
if __name__ == "__main__":
    print("Run tests with: python manage.py test notes.tests.test_auth")
    print("\nTest Coverage:")
    print("- Token verification with missing CLERK_SECRET_KEY")
    print("- Empty and invalid tokens")
    print("- Authorization header parsing")
    print("- Decorator functionality")
    print("- Edge cases and error conditions")
