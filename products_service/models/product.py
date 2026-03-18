from sqlalchemy import Column, Integer, String, Float, Boolean
from app.db.base import Base

class Product(Base):
    __tablename__ = "products"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, nullable=False, index=True)
    name = Column(String, index=True)
    description = Column(String, nullable=True)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)