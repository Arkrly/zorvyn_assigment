"""Unit tests for user schemas."""
import pytest
from datetime import datetime
from app.schemas.user import UserRole, UserUpdate, UserResponse, UserList


class TestUserRole:
    """Tests for UserRole enum."""

    def test_user_role_values(self):
        """Test UserRole has correct values."""
        assert UserRole.VIEWER.value == "VIEWER"
        assert UserRole.ANALYST.value == "ANALYST"
        assert UserRole.ADMIN.value == "ADMIN"

    def test_user_role_members(self):
        """Test UserRole has all expected members."""
        assert len(UserRole) == 3


class TestUserUpdate:
    """Tests for UserUpdate schema."""

    def test_user_update_optional_fields(self):
        """Test UserUpdate allows optional role and is_active."""
        user_update = UserUpdate()
        assert user_update.role is None
        assert user_update.is_active is None

    def test_user_update_with_role(self):
        """Test UserUpdate accepts role."""
        user_update = UserUpdate(role=UserRole.ADMIN)
        assert user_update.role == UserRole.ADMIN

    def test_user_update_with_is_active(self):
        """Test UserUpdate accepts is_active."""
        user_update = UserUpdate(is_active=False)
        assert user_update.is_active is False

    def test_user_update_with_both(self):
        """Test UserUpdate accepts both fields."""
        user_update = UserUpdate(role=UserRole.ANALYST, is_active=True)
        assert user_update.role == UserRole.ANALYST
        assert user_update.is_active is True


class TestUserResponse:
    """Tests for UserResponse schema."""

    def test_user_response_from_attributes(self):
        """Test UserResponse can be created from model."""
        user_data = {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "email": "test@example.com",
            "name": "Test User",
            "role": "VIEWER",
            "is_active": True,
            "is_deleted": False,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "updated_by": None,
        }
        response = UserResponse(**user_data)
        assert response.email == "test@example.com"
        assert response.role == "VIEWER"

    def test_user_response_with_optional_name(self):
        """Test UserResponse handles optional name."""
        user_data = {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "email": "test@example.com",
            "name": None,
            "role": "VIEWER",
            "is_active": True,
            "is_deleted": False,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "updated_by": None,
        }
        response = UserResponse(**user_data)
        assert response.name is None