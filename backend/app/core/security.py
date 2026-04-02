"""Security utilities for password hashing and verification."""
from pwdlib import PasswordHash

# Recommended hash configuration (Argon2id)
password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """Hash password using Argon2id."""
    return password_hash.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    """Verify password against hash."""
    return password_hash.verify(plain, hashed)


# Dummy hash for timing-safe authentication
# This is used to prevent timing attacks when user doesn't exist
DUMMY_HASH = "$argon2id$v=19$m=65536,t=3,p=4$YXJrd3MtdGVzdC1kdW1teS1oYXNo$ZHVtbXktaGFzaC10by1wcmV2ZW50LXRpbWluZy1hdHRhY2tz"