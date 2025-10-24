from sqlalchemy import Column, Integer, String, Float, Boolean
from app.db.base import Base
from sqlalchemy.orm import relationship

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, nullable=True)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    
    # Relationship with Orders
    orders = relationship("Orders", back_populates="product")