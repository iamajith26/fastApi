from pydantic import BaseModel
from typing import Optional

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    quantity: int
    is_active: bool = True

class ProductCreate(ProductBase):
    # Inherits from ProductBase but excludes id (auto-generated)
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    quantity: Optional[int] = None

class ProductOut(ProductBase):
    id: int  # Only include id in output schema
    
    class Config:
        from_attributes = True   # Pydantic v2