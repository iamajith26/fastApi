from pydantic import BaseModel
from datetime import date  # Import date for the order_date field
from typing import Optional

class OrderBase(BaseModel):
    id: int
    product_id: int
    customer_id: int
    order_date: date
    status: str
    
class OrderCreate(OrderBase):
    pass

class OrderUpdate(BaseModel):
    product_id: Optional[int] = None
    customer_id: Optional[int] = None
    order_date: Optional[date] = None
    status: Optional[str] = None    

class OrderOut(BaseModel):
    id: int
    order_date: date
    product_name: Optional[str]
    customer_name: Optional[str]
    status: str

    class Config:
        orm_mode = True
        
class OrderUpdateTotal(BaseModel):
    amount: float
    o_id: int