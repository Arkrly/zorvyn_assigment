"""Unit tests for config module."""
import pytest
from app.core.config import Settings


class TestConfig:
    """Tests for application configuration."""

    def test_settings_with_valid_env(self, monkeypatch):
        """Test Settings loads correctly with valid environment variables."""
        monkeypatch.setenv("DATABASE_URL", "sqlite+aiosqlite:///test.db")
        monkeypatch.setenv("SECRET_KEY", "test-secret-key-123")
        
        settings = Settings()
        assert settings.DATABASE_URL == "sqlite+aiosqlite:///test.db"
        assert settings.SECRET_KEY == "test-secret-key-123"
        assert settings.DEBUG is False
        assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 30
        assert settings.ALGORITHM == "HS256"

    def test_settings_default_values(self, monkeypatch):
        """Test Settings has correct default values."""
        monkeypatch.setenv("DATABASE_URL", "sqlite+aiosqlite:///test.db")
        monkeypatch.setenv("SECRET_KEY", "test-secret-key-123")
        
        settings = Settings()
        assert settings.DEBUG is False
        assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 30
        assert settings.REFRESH_TOKEN_EXPIRE_DAYS == 7
        assert settings.ALGORITHM == "HS256"

    def test_settings_debug_true(self, monkeypatch):
        """Test DEBUG can be set to True."""
        monkeypatch.setenv("DATABASE_URL", "sqlite+aiosqlite:///test.db")
        monkeypatch.setenv("SECRET_KEY", "test-secret-key-123")
        monkeypatch.setenv("DEBUG", "true")
        
        settings = Settings()
        assert settings.DEBUG is True