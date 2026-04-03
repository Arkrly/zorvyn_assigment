"""Unit tests for security module."""
import pytest
from app.core.security import hash_password, verify_password, DUMMY_HASH


class TestPasswordHashing:
    """Tests for password hashing functions."""

    def test_hash_password_returns_string(self):
        """Test that hash_password returns a hash string."""
        result = hash_password("testpassword123")
        assert isinstance(result, str)
        assert result != "testpassword123"

    def test_hash_password_unique_hashes(self):
        """Test that same password produces different hashes (salt)."""
        hash1 = hash_password("mypassword")
        hash2 = hash_password("mypassword")
        assert hash1 != hash2

    def test_verify_password_correct(self):
        """Test that verify_password returns True for correct password."""
        password = "securepassword123"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Test that verify_password returns False for wrong password."""
        password = "correctpassword"
        wrong_password = "wrongpassword"
        hashed = hash_password(password)
        assert verify_password(wrong_password, hashed) is False

    def test_verify_password_against_dummy(self):
        """Test verify_password handles dummy hash correctly."""
        result = verify_password("anypassword", DUMMY_HASH)
        assert isinstance(result, bool)