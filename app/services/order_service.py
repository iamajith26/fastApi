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
        
    # def get_all_orders(self):
        # # Raw SQL query to join Orders, Products, and Customers
        # query = text("""
        #     SELECT 
        #         o.id AS id,  -- Ensure the alias matches the schema
        #         o.order_date,
        #         o.status,
        #         o.customer_id,
        #         o.product_id,
        #         p.name AS product_name,
        #         c.name AS customer_name
        #     FROM orders o
        #     JOIN products p ON o.product_id = p.id
        #     JOIN customer c ON o.customer_id = c.id
        # """)
        # result = self.db.execute(query).fetchall()

        ## Convert result to a list of dictionaries
        # orders = [
        #         {
        #             "id": row.id,
        #             "order_date": row.order_date,
        #             "status": row.status,
        #             "customer_id": row.customer_id,
        #             "product_id": row.product_id,
        #             "product_name": row.product_name if row.product_name else "Unknown Product",
        #             "customer_name": row.customer_name if row.customer_name else "Unknown Customer",
        #         }
        #         for row in result
        #     ]
        # return orders

    def get_all_orders(self):
        # ORM query to join Orders, Products, and Customers
        orders = (
            self.db.query(
                Orders.id,
                Orders.order_date,
                Orders.status,
                Orders.customer_id,
                Orders.product_id,
                Product.name.label("product_name"),
                Customer.name.label("customer_name"),
            )
            .join(Product, Orders.product_id == Product.id)
            .join(Customer, Orders.customer_id == Customer.id)
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
            }
            for order in orders
        ]
    
    def get_order_by_id(self, order_id: int):
        # ORM query to join Orders, Products, and Customers
        order = (
            self.db.query(
                Orders.id,
                Orders.order_date,
                Orders.status,
                Orders.customer_id,
                Orders.product_id,
                Product.name.label("product_name"),
                Customer.name.label("customer_name"),
            )
            .join(Product, Orders.product_id == Product.id)
            .join(Customer, Orders.customer_id == Customer.id)
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
        }

def get_order_service(db: Session = Depends(get_db)) -> OrderService:
    return OrderService(db)