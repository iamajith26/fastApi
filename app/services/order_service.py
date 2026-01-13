from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
from app.db.session import get_db
from app.models.orders import Orders
from app.schemas.orders import OrderCreate, OrderUpdate
from app.models.orders import Orders
from app.models.product import Product
from app.models.user import Customer
from sqlalchemy import text

class OrderService:
    def __init__(self, db: Session):
        self.db = db
        
    def get_all_orders(self):
        # ORM query to join Orders, Products, Customers, and OrderDetails
        from app.models.orders import OrderDetails
        orders = (
            self.db.query(
                Orders.id,
                Orders.order_date,
                Orders.status,
                Orders.customer_id,
                Orders.product_id,
                Product.name.label("product_name"),
                Customer.name.label("customer_name"),
                OrderDetails.quantity,
            )
            .join(Product, Orders.product_id == Product.id)
            .join(Customer, Orders.customer_id == Customer.id)
            .join(OrderDetails, Orders.id == OrderDetails.order_id)
            .all()
        )
        
        # Convert result to a list of dictionaries
        return [
            {
                "id": order.id,
                "order_date": order.order_date,
                "status": order.status,
                "customer_id": order.customer_id,
                "product_id": order.product_id,
                "product_name": order.product_name,
                "customer_name": order.customer_name,
                "quantity": order.quantity,
            }
            for order in orders
        ]
    
    def get_order_by_id(self, order_id: int):
        # ORM query to join Orders, Products, Customers, and OrderDetails
        from app.models.orders import OrderDetails
        order = (
            self.db.query(
                Orders.id,
                Orders.order_date,
                Orders.status,
                Orders.customer_id,
                Orders.product_id,
                Product.name.label("product_name"),
                Customer.name.label("customer_name"),
                OrderDetails.quantity,
            )
            .join(Product, Orders.product_id == Product.id)
            .join(Customer, Orders.customer_id == Customer.id)
            .join(OrderDetails, Orders.id == OrderDetails.order_id)
            .filter(Orders.id == order_id)
            .first()
        )

        if order is None:
            raise HTTPException(status_code=404, detail="Order not found")

        # Convert result to a dictionary
        return {
            "id": order.id,
            "order_date": order.order_date,
            "status": order.status,
            "customer_id": order.customer_id,
            "product_id": order.product_id,
            "product_name": order.product_name,
            "customer_name": order.customer_name,
            "quantity": order.quantity,
        }
        
    def order_create(self, order_data: OrderCreate):
        # First, get the product to calculate total
        product = self.db.query(Product).filter(Product.id == order_data.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Create the order
        new_order = Orders(
            product_id=order_data.product_id,
            customer_id=order_data.customer_id,
            order_date=order_data.order_date,
            status=order_data.status,
        )
        self.db.add(new_order)
        self.db.commit()
        self.db.refresh(new_order)
        
        # Calculate total for order details
        total_amount = product.price * order_data.quantity
        
        # Create order details
        from app.models.orders import OrderDetails
        order_detail = OrderDetails(
            order_id=new_order.id,
            quantity=order_data.quantity,
            total=total_amount
        )
        self.db.add(order_detail)
        self.db.commit()
        self.db.refresh(order_detail)
        
        return new_order

def get_order_service(db: Session = Depends(get_db)) -> OrderService:
    return OrderService(db)