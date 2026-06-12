"""
Clerk authentication utilities for JWT verification.
"""

import os
import logging
import jwt
from functools import wraps

from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed

logger = logging.getLogger(__name__)

CLERK_SECRET_KEY = os.getenv("CLERK_SECRET_KEY")


def get_clerk_user_from_token(token: str) -> str:
    """
    Verify a Clerk JWT token and extract the user ID.

    Args:
        token: The JWT token from the Authorization header

    Returns:
        The Clerk user ID (sub claim)

    Raises:
        AuthenticationFailed: If token is invalid, expired, or missing required claims
    """
    if not CLERK_SECRET_KEY:
        logger.error("CLERK_SECRET_KEY environment variable not set")
        raise AuthenticationFailed("Authentication not configured")

    if not token:
        raise AuthenticationFailed("No authentication token provided")

    try:
        # Decode and verify JWT using PyJWT
        # Clerk uses RS256 (asymmetric) for JWTs, we verify using the secret key
        decoded = jwt.decode(
            token,
            CLERK_SECRET_KEY,
            algorithms=["HS256", "RS256"],  # Support both symmetric and asymmetric
            options={"verify_signature": True}
        )

        user_id = decoded.get("sub")
        if not user_id:
            logger.warning("Token missing 'sub' (user ID) claim")
            raise AuthenticationFailed("Invalid token: missing user ID claim")

        return user_id

    except jwt.DecodeError as e:
        logger.warning(f"JWT decode error: {str(e)}")
        raise AuthenticationFailed(f"Invalid token format: {str(e)}")
    except jwt.ExpiredSignatureError as e:
        logger.warning(f"Token expired: {str(e)}")
        raise AuthenticationFailed("Token has expired")
    except jwt.InvalidSignatureError as e:
        logger.warning(f"Invalid token signature: {str(e)}")
        raise AuthenticationFailed("Invalid token signature")
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token: {str(e)}")
        raise AuthenticationFailed(f"Invalid token: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected token verification error: {str(e)}")
        raise AuthenticationFailed(f"Token verification failed: {str(e)}")


def get_clerk_user_from_request(request) -> str:
    """
    Extract and verify Clerk user ID from request Authorization header.

    Args:
        request: Django request object

    Returns:
        The Clerk user ID

    Raises:
        AuthenticationFailed: If no token or token is invalid
    """
    auth_header = request.META.get("HTTP_AUTHORIZATION", "")

    if not auth_header:
        raise AuthenticationFailed("Authorization header missing")

    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise AuthenticationFailed("Invalid Authorization header format. Use 'Bearer <token>'")

    token = parts[1]
    return get_clerk_user_from_token(token)


def require_auth(view_func):
    """
    Decorator to require authentication on a view.
    Adds user_clerk_id to request object.
    """
    @wraps(view_func)
    def wrapped(request, *args, **kwargs):
        try:
            user_clerk_id = get_clerk_user_from_request(request)
            request.user_clerk_id = user_clerk_id
            return view_func(request, *args, **kwargs)
        except AuthenticationFailed as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_401_UNAUTHORIZED
            )
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return Response(
                {"error": "Authentication failed"},
                status=status.HTTP_401_UNAUTHORIZED
            )

    return wrapped
