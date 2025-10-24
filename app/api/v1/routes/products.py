from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.product import ProductCreate, ProductUpdate, ProductOut
from app.services.product_service import ProductService, get_product_service

router = APIRouter()

@router.get("/", response_model=list[ProductOut])
def list_products(
    product_service: ProductService = Depends(get_product_service),
):
    return product_service.get_all_products()

@router.get("/{product_id}", response_model=ProductOut)
def read_product(
    product_id: int,
    product_service: ProductService = Depends(get_product_service),
):
    product = product_service.get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.post("/", response_model=dict)
def create_product(
    product: ProductCreate,
    product_service: ProductService = Depends(get_product_service),
):
    return {"message": "Product created successfully"}

@router.put("/{product_id}", response_model=ProductOut)
def update_product(
    product_id: int,
    product: ProductUpdate,
    product_service: ProductService = Depends(get_product_service),
):
    updated = product_service.update_product(product_id, product)
    if not updated:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product updated successfully"}

@router.delete("/{product_id}", response_model=dict)
def delete_product(
    product_id: int,
    product_service: ProductService = Depends(get_product_service),
):
    ok = product_service.delete_product(product_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted successfully"}