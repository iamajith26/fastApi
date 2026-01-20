from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.db.session import get_db
from app.dependencies.gateway_auth import validate_gateway_request
from sqlalchemy.orm import Session
from cart_service.services.cart_service import get_cart_service, CartService
from cart_service.schemas.cart import AddToCartRequest, UpdateCartItemRequest, CartMergeRequest, CartOut
from typing import Optional
import logging
import os

app = FastAPI(
    title="Cart Microservice",
    description="Microservice for shopping cart management",
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

def get_cart_service_with_user(
    user_context: dict = Depends(validate_gateway_request),
    db: Session = Depends(get_db)
) -> CartService:
    """Get CartService with user context"""
    user_id = str(user_context.get("user_id"))
    return CartService(db, user_id=user_id)

# Public cart routes (for guest users with session)
@app.get("/cart/guest/{session_id}")
async def get_guest_cart(
    session_id: str,
    cart_service: CartService = Depends(get_cart_service)
):
    """Get cart for guest user by session ID"""
    cart = await cart_service.get_cart(session_id=session_id)
    if not cart:
        return {"message": "No cart found for this session", "cart": None}
    return cart

@app.post("/cart/guest/{session_id}/add")
async def add_to_guest_cart(
    session_id: str,
    request: AddToCartRequest,
    cart_service: CartService = Depends(get_cart_service)
):
    """Add item to guest cart"""
    return await cart_service.add_to_cart(request, session_id=session_id)

@app.put("/cart/guest/{session_id}/items/{item_id}")
async def update_guest_cart_item(
    session_id: str,
    item_id: int,
    request: UpdateCartItemRequest,
    cart_service: CartService = Depends(get_cart_service)
):
    """Update item quantity in guest cart"""
    return cart_service.update_cart_item(item_id, request, session_id=session_id)

@app.delete("/cart/guest/{session_id}/items/{item_id}")
async def remove_from_guest_cart(
    session_id: str,
    item_id: int,
    cart_service: CartService = Depends(get_cart_service)
):
    """Remove item from guest cart"""
    return cart_service.remove_from_cart(item_id, session_id=session_id)

@app.delete("/cart/guest/{session_id}/clear")
async def clear_guest_cart(
    session_id: str,
    cart_service: CartService = Depends(get_cart_service)
):
    """Clear all items from guest cart"""
    return cart_service.clear_cart(session_id=session_id)

# Protected cart routes (for authenticated users)
@app.get("/cart/")
async def get_user_cart(
    user_context: dict = Depends(validate_gateway_request),
    cart_service: CartService = Depends(get_cart_service_with_user)
):
    """Get cart for authenticated user"""
    user_id = user_context.get("user_id")
    cart = await cart_service.get_cart(user_id=user_id)
    if not cart:
        return {"message": "No cart found for this user", "cart": None}
    return cart

@app.post("/cart/add")
async def add_to_user_cart(
    request: AddToCartRequest,
    user_context: dict = Depends(validate_gateway_request),
    cart_service: CartService = Depends(get_cart_service_with_user)
):
    """Add item to authenticated user's cart"""
    user_id = user_context.get("user_id")
    return await cart_service.add_to_cart(request, user_id=user_id)

@app.put("/cart/items/{item_id}")
async def update_user_cart_item(
    item_id: int,
    request: UpdateCartItemRequest,
    user_context: dict = Depends(validate_gateway_request),
    cart_service: CartService = Depends(get_cart_service_with_user)
):
    """Update item quantity in authenticated user's cart"""
    user_id = user_context.get("user_id")
    return cart_service.update_cart_item(item_id, request, user_id=user_id)

@app.delete("/cart/items/{item_id}")
async def remove_from_user_cart(
    item_id: int,
    user_context: dict = Depends(validate_gateway_request),
    cart_service: CartService = Depends(get_cart_service_with_user)
):
    """Remove item from authenticated user's cart"""
    user_id = user_context.get("user_id")
    return cart_service.remove_from_cart(item_id, user_id=user_id)

@app.delete("/cart/clear")
async def clear_user_cart(
    user_context: dict = Depends(validate_gateway_request),
    cart_service: CartService = Depends(get_cart_service_with_user)
):
    """Clear all items from authenticated user's cart"""
    user_id = user_context.get("user_id")
    return cart_service.clear_cart(user_id=user_id)

@app.post("/cart/merge")
async def merge_guest_cart(
    request: CartMergeRequest,
    user_context: dict = Depends(validate_gateway_request),
    cart_service: CartService = Depends(get_cart_service_with_user)
):
    """Merge guest cart into authenticated user's cart"""
    user_id = user_context.get("user_id")
    return cart_service.merge_cart(user_id, request.session_id)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "cart"}