import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.deps import get_db
from app.models import Base

# Use in-memory SQLite for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


Base.metadata.create_all(bind=engine)
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_register():
    """Test user registration."""
    response = client.post(
        "/auth/register",
        json={"email": "test@example.com", "password": "testpassword123"},
    )
    assert response.status_code == 201
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()


def test_register_duplicate_email():
    """Test registration with duplicate email."""
    # First registration
    client.post(
        "/auth/register",
        json={"email": "duplicate@example.com", "password": "testpassword123"},
    )

    # Second registration with same email
    response = client.post(
        "/auth/register",
        json={"email": "duplicate@example.com", "password": "testpassword456"},
    )
    assert response.status_code == 400


def test_login():
    """Test user login."""
    # Register first
    client.post(
        "/auth/register",
        json={"email": "login@example.com", "password": "testpassword123"},
    )

    # Login
    response = client.post(
        "/auth/login",
        json={"email": "login@example.com", "password": "testpassword123"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_invalid_password():
    """Test login with wrong password."""
    # Register first
    client.post(
        "/auth/register",
        json={"email": "wrongpwd@example.com", "password": "testpassword123"},
    )

    # Login with wrong password
    response = client.post(
        "/auth/login",
        json={"email": "wrongpwd@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
