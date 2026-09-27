import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from argon2 import PasswordHasher
from jose import jwt

from app.core.config import settings


# Password hashing object
password_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    # Convert plain password into a secure Argon2 hash
    return password_hasher.hash(password)


def verify_password(
    password: str,
    password_hash: str,
) -> bool:
    # Compare entered password with stored Argon2 hash
    try:
        return password_hasher.verify(
            password_hash,
            password,
        )
    except Exception:
        return False


def generate_verification_token() -> str:
    # Generate a secure random token for email verification
    return secrets.token_urlsafe(32)


def hash_verification_token(token: str) -> str:
    # Hash the verification token before storing it
    return hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()

def create_access_token(
    user_id: int,
) -> str:

    # Calculate when the JWT should expire
    expire = (
        datetime.now(timezone.utc)
        + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )

    # Data that will be stored inside the JWT
    payload = {
        # Subject identifies the authenticated user
        "sub": str(user_id),

        # Identifies this token as an access token
        "type": "access",
        "exp": expire,
    }

    # Create and sign the JWT
    access_token = jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )

    return access_token

def generate_refresh_token() -> str:

    return secrets.token_urlsafe(64)


def hash_refresh_token(
    refresh_token: str,
) -> str:

    # Hash the refresh token before storing it in the database
    return hashlib.sha256(
        refresh_token.encode("utf-8")
    ).hexdigest()