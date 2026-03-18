from sqlalchemy import Column, Integer, Text, DateTime, String, Boolean
from app.db.base import Base
from datetime import datetime

class Customer(Base):
    __tablename__ = "customer"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    email = Column(String, index=True, unique=True, nullable=False)
    ph_no = Column(Integer, nullable=False)
    pincode = Column(Integer, nullable=False)
    hashed_password = Column(String, nullable=True)
    role_id = Column(Integer, nullable=True, default=2)
    is_active = Column(Boolean, default=True)
    
class TokenBlacklist(Base):
    __tablename__ = "token_blacklist"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    token = Column(Text, nullable=False, unique=True)
    blacklisted_at = Column(DateTime, default=datetime.utcnow)