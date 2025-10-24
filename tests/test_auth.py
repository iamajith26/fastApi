from fastapi.testclient import TestClient
from app.main import app
from app.models.user import Customer as User
from app.schemas.user import UserCreate
from app.auth.jwt_handler import create_access_token

client = TestClient(app)

def test_register_user():
    response = client.post("/api/v1/auth/register", json={"username": "testuser", "password": "testpassword"})
    assert response.status_code == 201
    assert response.json()["username"] == "testuser"

def test_login_user():
    # First, register the user
    client.post("/api/v1/auth/register", json={"username": "testuser", "password": "testpassword"})
    
    # Now, attempt to log in
    response = client.post("/api/v1/auth/login", json={"username": "testuser", "password": "testpassword"})
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_invalid_user():
    response = client.post("/api/v1/auth/login", json={"username": "invaliduser", "password": "wrongpassword"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"

def test_access_protected_route():
    # Register and log in to get a token
    client.post("/api/v1/auth/register", json={"username": "testuser", "password": "testpassword"})
    login_response = client.post("/api/v1/auth/login", json={"username": "testuser", "password": "testpassword"})
    token = login_response.json()["access_token"]

    # Access a protected route
    response = client.get("/api/v1/protected-route", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["message"] == "Access granted"

def test_access_protected_route_without_token():
    response = client.get("/api/v1/protected-route")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"