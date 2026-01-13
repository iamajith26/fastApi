# This file ensures all models are imported so SQLAlchemy can resolve relationships
from app.models.user import Customer, TokenBlacklist
from app.models.product import Product
from app.models.orders import Orders, OrderDetails

# Make sure all models are available
__all__ = ["Customer", "TokenBlacklist", "Product", "Orders", "OrderDetails"]