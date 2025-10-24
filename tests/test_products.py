from fastapi.testclient import TestClient
from app.main import app
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate

client = TestClient(app)

def test_create_product():
    product_data = {"name": "Test Product", "description": "A product for testing", "price": 10.99}
    response = client.post("/api/v1/products/", json=product_data)
    assert response.status_code == 201
    assert response.json()["name"] == product_data["name"]

def test_read_product():
    response = client.get("/api/v1/products/1")
    assert response.status_code == 200
    assert "name" in response.json()

def test_update_product():
    update_data = {"name": "Updated Product", "description": "An updated product", "price": 12.99}
    response = client.put("/api/v1/products/1", json=update_data)
    assert response.status_code == 200
    assert response.json()["name"] == update_data["name"]

def test_delete_product():
    response = client.delete("/api/v1/products/1")
    assert response.status_code == 204

def test_list_products():
    response = client.get("/api/v1/products/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)