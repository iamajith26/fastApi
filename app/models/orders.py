from sqlalchemy import Column, Integer, Date, String, ForeignKey, Float, Boolean
from app.db.base import Base
from sqlalchemy.orm import relationship


class Orders(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    customer_id = Column(Integer, ForeignKey("customer.id"), nullable=True)
    order_date = Column(Date, nullable=True)
    status = Column(String, default="Pending", nullable=True)

    # Relationships
    product = relationship("Product", back_populates="orders")
    customer = relationship("Customer", back_populates="orders")
    order_details = relationship("OrderDetails", back_populates="order")  # Added relationship
    
class OrderDetails(Base):
    __tablename__ = 'order_details'
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    total = Column(Float, nullable=False)
    
    # Relationships
    order = relationship("Orders", back_populates="order_details")
