from sqlalchemy import Column, Integer, Date, String, ForeignKey, Float, Boolean
from app.db.base import Base
from sqlalchemy.orm import relationship


class Orders(Base):
    __tablename__ = "orders"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, nullable=True)  # Just store ID, no foreign key reference
    customer_id = Column(Integer, nullable=True)  # Just store ID, no foreign key reference
    order_date = Column(Date, nullable=True)
    status = Column(String, default="Pending", nullable=True)

    # Only relationship to models within this service
    order_details = relationship("OrderDetails", back_populates="order")
    
class OrderDetails(Base):
    __tablename__ = 'order_details'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    total = Column(Float, nullable=False)
    
    # Relationships
    order = relationship("Orders", back_populates="order_details")