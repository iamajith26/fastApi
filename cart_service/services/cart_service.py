from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
from app.db.session import get_db
from cart_service.models.cart import Cart, CartItem
from cart_service.schemas.cart import CartCreate, CartItemCreate, CartItemUpdate, AddToCartRequest
from typing import Optional, Dict, Any
from decimal import Decimal
import httpx
import os
import logging

logger = logging.getLogger(__name__)

# Microservice URLs
PRODUCTS_SERVICE_URL = os.getenv("PRODUCTS_SERVICE_URL", "http://localhost:8001")

class CartService:
    def __init__(self, db: Session, user_id: str = None):
        self.db = db
        self.user_id = user_id
        
    async def get_product_info(self, product_id: int) -> Optional[Dict[str, Any]]:
        """Get product information from products service"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                headers = {}
                if self.user_id:
                    headers["x-user-id"] = self.user_id
                
                response = await client.get(
                    f"{PRODUCTS_SERVICE_URL}/products/{product_id}",
                    headers=headers
                )
                if response.status_code == 200:
                    return response.json()
                return None
        except Exception as e:
            logger.error(f"Error fetching product {product_id}: {e}")
            return None
    
    def get_or_create_cart(self, user_id: Optional[int] = None, session_id: Optional[str] = None) -> Cart:
        """Get existing cart or create new one for user or session"""
        if user_id:
            cart = self.db.query(Cart).filter(
                Cart.user_id == user_id, 
                Cart.is_active == True
            ).first()
        elif session_id:
            cart = self.db.query(Cart).filter(
                Cart.session_id == session_id, 
                Cart.is_active == True
            ).first()
        else:
            raise HTTPException(status_code=400, detail="Either user_id or session_id required")
        
        if not cart:
            cart = Cart(user_id=user_id, session_id=session_id)
            self.db.add(cart)
            self.db.commit()
            self.db.refresh(cart)
        
        return cart
    
    async def add_to_cart(self, request: AddToCartRequest, user_id: Optional[int] = None, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Add item to cart"""
        # Verify product exists and get price
        product_info = await self.get_product_info(request.product_id)
        if not product_info:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Get or create cart
        cart = self.get_or_create_cart(user_id=user_id, session_id=session_id)
        
        # Check if item already exists in cart
        existing_item = self.db.query(CartItem).filter(
            CartItem.cart_id == cart.id,
            CartItem.product_id == request.product_id
        ).first()
        
        if existing_item:
            # Update quantity
            existing_item.quantity += request.quantity
            self.db.commit()
            self.db.refresh(existing_item)
            return {"message": "Cart item quantity updated", "item_id": existing_item.id}
        else:
            # Add new item
            cart_item = CartItem(
                cart_id=cart.id,
                product_id=request.product_id,
                quantity=request.quantity,
                price=Decimal(str(product_info["price"]))
            )
            self.db.add(cart_item)
            self.db.commit()
            self.db.refresh(cart_item)
            return {"message": "Item added to cart", "item_id": cart_item.id}
    
    def update_cart_item(self, cart_item_id: int, update: CartItemUpdate, user_id: Optional[int] = None, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Update cart item quantity"""
        # Get cart item and verify ownership
        cart_item = self.db.query(CartItem).join(Cart).filter(
            CartItem.id == cart_item_id,
            Cart.is_active == True
        ).first()
        
        if not cart_item:
            raise HTTPException(status_code=404, detail="Cart item not found")
        
        # Verify ownership
        if user_id and cart_item.cart.user_id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to modify this cart item")
        elif session_id and cart_item.cart.session_id != session_id:
            raise HTTPException(status_code=403, detail="Not authorized to modify this cart item")
        
        cart_item.quantity = update.quantity
        self.db.commit()
        self.db.refresh(cart_item)
        
        return {"message": "Cart item updated", "item_id": cart_item.id}
    
    def remove_from_cart(self, cart_item_id: int, user_id: Optional[int] = None, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Remove item from cart"""
        # Get cart item and verify ownership
        cart_item = self.db.query(CartItem).join(Cart).filter(
            CartItem.id == cart_item_id,
            Cart.is_active == True
        ).first()
        
        if not cart_item:
            raise HTTPException(status_code=404, detail="Cart item not found")
        
        # Verify ownership
        if user_id and cart_item.cart.user_id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to modify this cart item")
        elif session_id and cart_item.cart.session_id != session_id:
            raise HTTPException(status_code=403, detail="Not authorized to modify this cart item")
        
        self.db.delete(cart_item)
        self.db.commit()
        
        return {"message": "Item removed from cart"}
    
    async def get_cart(self, user_id: Optional[int] = None, session_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get cart with enriched product information"""
        if user_id:
            cart = self.db.query(Cart).filter(
                Cart.user_id == user_id,
                Cart.is_active == True
            ).first()
        elif session_id:
            cart = self.db.query(Cart).filter(
                Cart.session_id == session_id,
                Cart.is_active == True
            ).first()
        else:
            raise HTTPException(status_code=400, detail="Either user_id or session_id required")
        
        if not cart:
            return None
        
        # Enrich cart items with product information
        enriched_items = []
        total_quantity = 0
        total_amount = Decimal('0.00')
        
        for item in cart.items:
            product_info = await self.get_product_info(item.product_id)
            
            enriched_item = {
                "id": item.id,
                "cart_id": item.cart_id,
                "product_id": item.product_id,
                "quantity": item.quantity,
                "price": item.price,
                "added_at": item.added_at,
                "updated_at": item.updated_at,
                "product_name": product_info.get("name") if product_info else "Unknown Product"
            }
            enriched_items.append(enriched_item)
            total_quantity += item.quantity
            total_amount += item.price * item.quantity
        
        return {
            "id": cart.id,
            "user_id": cart.user_id,
            "session_id": cart.session_id,
            "created_at": cart.created_at,
            "updated_at": cart.updated_at,
            "is_active": cart.is_active,
            "items": enriched_items,
            "item_count": len(enriched_items),
            "total_quantity": total_quantity,
            "total_amount": total_amount
        }
    
    def clear_cart(self, user_id: Optional[int] = None, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Clear all items from cart"""
        if user_id:
            cart = self.db.query(Cart).filter(
                Cart.user_id == user_id,
                Cart.is_active == True
            ).first()
        elif session_id:
            cart = self.db.query(Cart).filter(
                Cart.session_id == session_id,
                Cart.is_active == True
            ).first()
        else:
            raise HTTPException(status_code=400, detail="Either user_id or session_id required")
        
        if not cart:
            raise HTTPException(status_code=404, detail="Cart not found")
        
        # Delete all items in cart
        self.db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
        self.db.commit()
        
        return {"message": "Cart cleared successfully"}
    
    def merge_cart(self, user_id: int, session_id: str) -> Dict[str, Any]:
        """Merge guest cart into user cart upon login"""
        # Get guest cart
        guest_cart = self.db.query(Cart).filter(
            Cart.session_id == session_id,
            Cart.is_active == True
        ).first()
        
        if not guest_cart:
            return {"message": "No guest cart to merge"}
        
        # Get or create user cart
        user_cart = self.get_or_create_cart(user_id=user_id)
        
        # Merge items
        merged_items = 0
        for guest_item in guest_cart.items:
            # Check if user cart already has this product
            existing_item = self.db.query(CartItem).filter(
                CartItem.cart_id == user_cart.id,
                CartItem.product_id == guest_item.product_id
            ).first()
            
            if existing_item:
                # Merge quantities
                existing_item.quantity += guest_item.quantity
            else:
                # Move item to user cart
                guest_item.cart_id = user_cart.id
            
            merged_items += 1
        
        # Deactivate guest cart
        guest_cart.is_active = False
        
        self.db.commit()
        
        return {"message": f"Successfully merged {merged_items} items from guest cart"}

def get_cart_service(db: Session = Depends(get_db)) -> CartService:
    return CartService(db)