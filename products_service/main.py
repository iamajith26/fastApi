from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.db.session import get_db
from app.dependencies.gateway_auth import validate_gateway_request
from app.dependencies.gateway_auth import require_admin_role
from products_service.services.product_service import get_product_service, ProductService
from products_service.schemas.product import ProductCreate, ProductUpdate, ProductOut
from typing import Optional, List
import logging
import os

app = FastAPI(
    title="Products Microservice",
    description="Microservice for product management",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

logger = logging.getLogger(__name__)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Public Products Routes (No Authentication Required)
@app.get("/products/", response_model=List[ProductOut])
async def get_products(
    skip: int = 0,
    limit: int = 100,
    product_service: ProductService = Depends(get_product_service)
):
    """Get all products with pagination - Public endpoint"""
    products = product_service.get_all_products()
    # Apply pagination manually since get_all_products doesn't support it yet
    return products[skip:skip + limit]

@app.get("/products/{product_id}", response_model=ProductOut)
async def get_product(
    product_id: int,
    product_service: ProductService = Depends(get_product_service)
):
    """Get a specific product by ID - Public endpoint"""
    product = product_service.get_product(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

# Protected Products Routes (Authentication Required)
@app.post("/products/", response_model=dict)
async def create_product(
    product: ProductCreate,
    user_context: dict = Depends(validate_gateway_request),
    is_admin = Depends(require_admin_role),
    product_service: ProductService = Depends(get_product_service)
):
    """Create a new product - Requires authentication"""
    product_service.create_product(product)
    logger.info(f"Product created by user ID: {user_context['user_id']}")
    return {"message": "Product created successfully"}

@app.put("/products/{product_id}", response_model=dict)
async def update_product(
    product_id: int,
    product_update: ProductUpdate,
    user_context: dict = Depends(validate_gateway_request),
    is_admin: bool = Depends(require_admin_role),
    product_service: ProductService = Depends(get_product_service)
):
    """Update a product - Requires authentication"""
    updated_product = product_service.update_product(product_id, product_update)
    if updated_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    logger.info(f"Product {product_id} updated by user ID: {user_context['user_id']}")
    return {"message": "Product updated successfully"}

@app.delete("/products/{product_id}", response_model=dict)
async def delete_product(
    product_id: int,
    user_context: dict = Depends(validate_gateway_request),
    is_admin: bool = Depends(require_admin_role),
    product_service: ProductService = Depends(get_product_service)
):
    """Delete a product - Requires authentication"""
    result = product_service.delete_product(product_id)
    logger.info(f"Product {product_id} deleted by user ID: {user_context['user_id']}")
    return result

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "products"}