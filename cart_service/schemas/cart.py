from pydantic import BaseModel, validator
from typing import List, Optional
from datetime import datetime
from decimal import Decimal

class CartItemBase(BaseModel):
    product_id: int
    quantity: int
    price: Decimal

    @validator('quantity')
    def validate_quantity(cls, v):
        if v <= 0:
            raise ValueError('Quantity must be greater than 0')
        return v

class CartItemCreate(CartItemBase):
    pass

class CartItemUpdate(BaseModel):
    quantity: int
    
    @validator('quantity')
    def validate_quantity(cls, v):
        if v <= 0:
            raise ValueError('Quantity must be greater than 0')
        return v

class CartItemOut(CartItemBase):
    id: int
    cart_id: int
    added_at: datetime
    updated_at: datetime
    product_name: Optional[str] = None  # Will be populated from products service
    
    class Config:
        from_attributes = True

class CartCreate(BaseModel):
    user_id: Optional[int] = None
    session_id: Optional[str] = None

class CartOut(BaseModel):
    id: int
    user_id: Optional[int]
    session_id: Optional[str]
    created_at: datetime
    updated_at: datetime
    is_active: bool
    items: List[CartItemOut] = []
    item_count: int = 0
    total_quantity: int = 0
    total_amount: Decimal = 0
    
    class Config:
        from_attributes = True

class CartSummary(BaseModel):
    cart_id: int
    user_id: Optional[int]
    session_id: Optional[str]
    item_count: int
    total_quantity: int
    total_amount: Decimal
    
    class Config:
        from_attributes = True

class AddToCartRequest(BaseModel):
    product_id: int
    quantity: int = 1

    @validator('quantity')
    def validate_quantity(cls, v):
        if v <= 0:
            raise ValueError('Quantity must be greater than 0')
        return v

class UpdateCartItemRequest(BaseModel):
    quantity: int
    
    @validator('quantity')
    def validate_quantity(cls, v):
        if v <= 0:
            raise ValueError('Quantity must be greater than 0')
        return v

class CartMergeRequest(BaseModel):
    session_id: str