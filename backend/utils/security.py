"""
Security utilities for authentication and authorization.
"""
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from bson import ObjectId
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from config import Config
from services.mongo_service import mongo_service


class TokenError(HTTPException):
    """Custom exception for token-related errors."""

    def __init__(self, detail: str = "Could not validate credentials") -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


_bearer_scheme = HTTPBearer(auto_error=False)


def create_access_token(
    subject: str,
    expires_delta: Optional[timedelta] = None,
    additional_claims: Optional[Dict[str, Any]] = None,
) -> str:
    """Create a signed JWT access token."""
    if not subject:
        raise ValueError("Token subject cannot be empty")

    to_encode: Dict[str, Any] = {"sub": subject}
    if additional_claims:
        to_encode.update(additional_claims)

    expire = datetime.now(timezone.utc) + (
        expires_delta
        if expires_delta is not None
        else timedelta(minutes=Config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode["exp"] = expire

    return jwt.encode(
        to_encode,
        Config.JWT_SECRET_KEY,
        algorithm=Config.JWT_ALGORITHM,
    )


def decode_access_token(token: str) -> Dict[str, Any]:
    """Decode and validate a JWT access token."""
    try:
        payload = jwt.decode(
            token,
            Config.JWT_SECRET_KEY,
            algorithms=[Config.JWT_ALGORITHM],
        )
        return payload
    except JWTError as exc:
        raise TokenError("Invalid or expired token") from exc


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
) -> Dict[str, Any]:
    """Resolve and return the currently authenticated user."""
    if credentials is None:
        raise TokenError("Authentication credentials were not provided")

    token = credentials.credentials
    payload = decode_access_token(token)

    user_id = payload.get("sub")
    if not user_id:
        raise TokenError("Token payload missing subject")

    if not ObjectId.is_valid(user_id):
        raise TokenError("Invalid user identifier in token")

    if not mongo_service.is_connected():
        raise HTTPException(status_code=503, detail="Database not connected")

    users = mongo_service.get_collection("users")
    user = users.find_one({"_id": ObjectId(user_id), "is_active": True})
    if not user:
        raise TokenError("User not found or inactive")

    # Enrich with string id for convenience
    user["id"] = str(user["_id"])
    return user


def require_active_user(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Wrapper dependency to ensure the user account is active.
    """
    if not current_user.get("is_active", True):
        raise HTTPException(status_code=403, detail="User account is inactive")
    return current_user


def get_optional_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
) -> Optional[Dict[str, Any]]:
    """Return current user if token provided, otherwise None."""
    if credentials is None:
        return None
    try:
        return get_current_user(credentials)
    except TokenError:
        return None
    except HTTPException:
        return None


def get_optional_active_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
) -> Optional[Dict[str, Any]]:
    """Return active user if token valid, otherwise None."""
    user = get_optional_user(credentials)
    if user and not user.get("is_active", True):
        return None
    return user



