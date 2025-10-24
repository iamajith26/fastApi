from fastapi.testclient import TestClient
from app.main import app
from app.models.user import Customer as User
from app.schemas.user import UserCreate
from app.db.session import get_db
from sqlalchemy.orm import Session

client = TestClient(app)

def test_create_user():
    response = client.post("/api/v1/users/", json={"username": "testuser", "password": "testpassword"})
    assert response.status_code == 201
    assert response.json()["username"] == "testuser"

def test_get_user():
    # First create a user
    client.post("/api/v1/users/", json={"username": "testuser", "password": "testpassword"})
    
    # Now retrieve the user
    response = client.get("/api/v1/users/testuser")
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"

def test_update_user():
    # First create a user
    client.post("/api/v1/users/", json={"username": "testuser", "password": "testpassword"})
    
    # Now update the user
    response = client.put("/api/v1/users/testuser", json={"password": "newpassword"})
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"

def test_delete_user():
    # First create a user
    client.post("/api/v1/users/", json={"username": "testuser", "password": "testpassword"})
    
    # Now delete the user
    response = client.delete("/api/v1/users/testuser")
    assert response.status_code == 204

    # Verify the user is deleted
    response = client.get("/api/v1/users/testuser")
    assert response.status_code == 404