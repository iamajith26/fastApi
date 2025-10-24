from sqlalchemy import Column, Integer, Text, DateTime, String, Boolean
from app.db.base import Base
from sqlalchemy.orm import relationship
from datetime import datetime

class Customer(Base):
    __tablename__ = "customer"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    email = Column(String, index=True, unique=True, nullable=False)
    ph_no = Column(Integer, nullable=False)
    pincode = Column(Integer, nullable=False)
    hashed_password = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Relationship with Orders
    orders = relationship("Orders", back_populates="customer")
    
class TokenBlacklist(Base):
    __tablename__ = "token_blacklist"
    
    id = Column(Integer, primary_key=True, index=True)
    token = Column(Text, nullable=False, unique=True)
    blacklisted_at = Column(DateTime, default=datetime.utcnow)

