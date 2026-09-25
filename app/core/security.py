import hashlib
import secrets

from argon2 import PasswordHasher


# Create password hashing object
password_hasher = PasswordHasher()


# Convert a plain password into a secure hash
def hash_password(password: str) -> str:

    #generates the password hash
    return password_hasher.hash(password)


# Check whether a password matches the stored hash
def verify_password(password: str, password_hash: str) -> bool:

    try:

        return password_hasher.verify(password_hash, password)

    except Exception:
        return False


# Generate a secure random verification token
def generate_verification_token() -> str:

    # Generate a cryptographically secure random token
    return secrets.token_urlsafe(32)


# Convert the verification token into a SHA-256 hash
def hash_verification_token(token: str) -> str:

    # Encode the token and create its SHA-256 hash
    return hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()
