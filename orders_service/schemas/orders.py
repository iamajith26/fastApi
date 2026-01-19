from pydantic import BaseModel
from datetime import date  # Import date for the order_date field
from typing import Optional

class OrderBase(BaseModel):
    product_id: int
    customer_id: int
    order_date: date
    status: str
    quantity: int  # Added quantity field
    
class OrderCreate(OrderBase):
    pass

class OrderUpdate(BaseModel):
    product_id: Optional[int] = None
    customer_id: Optional[int] = None
    order_date: Optional[date] = None
    status: Optional[str] = None
    quantity: Optional[int] = None  # Added quantity to update schema

class OrderOut(BaseModel):
    id: int
    order_date: date
    product_name: Optional[str]
    customer_name: Optional[str]
    status: str
    quantity: int  # Added quantity to output schema

    class Config:
        from_attributes = True
        
class OrderUpdateTotal(BaseModel):
    amount: float
    o_id: int