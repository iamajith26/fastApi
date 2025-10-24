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