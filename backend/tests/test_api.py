"""Comprehensive API stress tests for FinanceBoard API."""
import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture(scope="function")
def client():
    """Create test client."""
    return TestClient(app)


def get_auth_header(client: TestClient, email: str, password: str) -> dict:
    """Helper to get authentication header."""
    response = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password}
    )
    if response.status_code == 200:
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    return {}


class TestHealthEndpoint:
    """Tests for health check endpoint."""

    def test_health_check(self, client):
        """Test health endpoint returns 200."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestAuthentication:
    """Tests for authentication endpoints."""

    def test_register_new_user(self, client):
        """Test user registration."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": f"test{__name__}@example.com",
                "password": "password123",
                "name": "Test User"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "user" in data
        assert "access_token" in data
        assert "refresh_token" in data

    def test_login_valid_credentials(self, client):
        """Test login with valid credentials."""
        email = f"login{__name__}@example.com"
        client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": "password123"}
        )
        response = client.post(
            "/api/v1/auth/login",
            data={"username": email, "password": "password123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_password(self, client):
        """Test login with invalid password fails."""
        email = f"wrongpass{__name__}@example.com"
        client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": "correctpassword"}
        )
        response = client.post(
            "/api/v1/auth/login",
            data={"username": email, "password": "wrongpassword"}
        )
        assert response.status_code == 401

    def test_login_nonexistent_user(self, client):
        """Test login with nonexistent user fails."""
        response = client.post(
            "/api/v1/auth/login",
            data={"username": f"nonexistent{__name__}@example.com", "password": "password123"}
        )
        assert response.status_code == 401

    def test_refresh_token(self, client):
        """Test token refresh."""
        email = f"refresh{__name__}@example.com"
        register_response = client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": "password123"}
        )
        refresh_token = register_response.json()["refresh_token"]
        
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    def test_refresh_invalid_token(self, client):
        """Test refresh with invalid token fails."""
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid_token"}
        )
        assert response.status_code == 401

    def test_get_current_user(self, client):
        """Test getting current user profile."""
        email = f"me{__name__}@example.com"
        client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": "password123", "name": "Me User"}
        )
        headers = get_auth_header(client, email, "password123")
        
        response = client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == email
        assert data["name"] == "Me User"
        assert data["role"] == "VIEWER"

    def test_get_current_user_unauthorized(self, client):
        """Test getting current user without auth fails."""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 401


class TestTransactions:
    """Tests for transaction endpoints."""

    def test_list_transactions(self, client):
        """Test listing transactions."""
        email = f"listtx{__name__}@example.com"
        client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": "password123"}
        )
        headers = get_auth_header(client, email, "password123")
        
        response = client.get("/api/v1/transactions", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data

    def test_list_transactions_unauthorized(self, client):
        """Test listing transactions without auth fails."""
        response = client.get("/api/v1/transactions")
        assert response.status_code == 401

    def test_viewer_cannot_create_transaction(self, client):
        """Test viewer cannot create transactions."""
        email = f"viewer_tx{__name__}@example.com"
        client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": "password123"}
        )
        headers = get_auth_header(client, email, "password123")
        
        response = client.post(
            "/api/v1/transactions",
            headers=headers,
            json={"type": "INCOME", "amount": 100, "category": "Test"}
        )
        assert response.status_code == 403


class TestUsers:
    """Tests for user management endpoints."""

    def test_list_users_forbidden(self, client):
        """Test listing users requires admin."""
        email = f"viewer_user{__name__}@example.com"
        client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": "password123"}
        )
        viewer_headers = get_auth_header(client, email, "password123")
        
        response = client.get("/api/v1/users", headers=viewer_headers)
        assert response.status_code == 403


class TestDashboard:
    """Tests for dashboard endpoints."""

    def test_get_summary(self, client):
        """Test getting dashboard summary."""
        email = f"dash{__name__}@example.com"
        client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": "password123"}
        )
        headers = get_auth_header(client, email, "password123")
        
        response = client.get("/api/v1/dashboard/summary", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "total_income" in data
        assert "total_expenses" in data
        assert "net_balance" in data
        assert "transaction_count" in data

    def test_get_categories(self, client):
        """Test getting category totals."""
        email = f"cat{__name__}@example.com"
        client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": "password123"}
        )
        headers = get_auth_header(client, email, "password123")
        
        response = client.get("/api/v1/dashboard/categories", headers=headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_trends(self, client):
        """Test getting monthly trends."""
        email = f"trends{__name__}@example.com"
        client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": "password123"}
        )
        headers = get_auth_header(client, email, "password123")
        
        response = client.get("/api/v1/dashboard/trends?months=6", headers=headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_recent(self, client):
        """Test getting recent transactions."""
        email = f"recent{__name__}@example.com"
        client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": "password123"}
        )
        headers = get_auth_header(client, email, "password123")
        
        response = client.get("/api/v1/dashboard/recent?limit=5", headers=headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_dashboard_unauthorized(self, client):
        """Test dashboard requires authentication."""
        response = client.get("/api/v1/dashboard/summary")
        assert response.status_code == 401


class TestErrorHandling:
    """Tests for error handling."""

    def test_invalid_email_format(self, client):
        """Test registration with invalid email format."""
        response = client.post(
            "/api/v1/auth/register",
            json={"email": "not-an-email", "password": "password123"}
        )
        assert response.status_code == 422

    def test_missing_required_fields(self, client):
        """Test registration with missing required fields."""
        response = client.post(
            "/api/v1/auth/register",
            json={"email": "test@example.com"}
        )
        assert response.status_code == 422