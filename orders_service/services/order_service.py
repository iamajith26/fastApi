from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
from app.db.session import get_db
from orders_service.models.orders import Orders, OrderDetails
from orders_service.schemas.orders import OrderCreate, OrderUpdate
from sqlalchemy import text
import httpx
import os
import logging

logger = logging.getLogger(__name__)

# Microservice URLs
PRODUCTS_SERVICE_URL = os.getenv("PRODUCTS_SERVICE_URL", "http://localhost:8001")
USERS_SERVICE_URL = os.getenv("USERS_SERVICE_URL", "http://localhost:8003")

class OrderService:
    def __init__(self, db: Session, user_id: str = None):
        self.db = db
        self.user_id = user_id
        
    async def get_product_info(self, product_id: int):
        """Get product information from products service"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                headers = {}
                if self.user_id:
                    headers["x-user-id"] = self.user_id
                
                response = await client.get(
                    f"{PRODUCTS_SERVICE_URL}/products/{product_id}",
                    headers=headers
                )
                if response.status_code == 200:
                    return response.json()
                return None
        except Exception as e:
            logger.error(f"Error fetching product {product_id}: {e}")
            return None
    
    async def get_customer_info(self, customer_id: int):
        """Get customer information from users service"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                headers = {}
                if self.user_id:
                    headers["x-user-id"] = self.user_id
                
                response = await client.get(
                    f"{USERS_SERVICE_URL}/users/{customer_id}",
                    headers=headers
                )
                if response.status_code == 200:
                    return response.json()
                return None
        except Exception as e:
            logger.error(f"Error fetching customer {customer_id}: {e}")
            return None
        
    async def get_all_orders(self):
        # Get orders with order details from our own database
        orders_query = (
            self.db.query(
                Orders.id,
                Orders.order_date,
                Orders.status,
                Orders.customer_id,
                Orders.product_id,
                OrderDetails.quantity,
            )
            .join(OrderDetails, Orders.id == OrderDetails.order_id)
            .all()
        )
        
        # Enrich with product and customer data from other services
        enriched_orders = []
        for order in orders_query:
            product_info = await self.get_product_info(order.product_id)
            customer_info = await self.get_customer_info(order.customer_id)
            
            enriched_orders.append({
                "id": order.id,
                "order_date": order.order_date,
                "status": order.status,
                "customer_id": order.customer_id,
                "product_id": order.product_id,
                "product_name": product_info.get("name") if product_info else "Unknown Product",
                "customer_name": customer_info.get("name") if customer_info else "Unknown Customer",
                "quantity": order.quantity,
            })
        
        return enriched_orders
    
    async def get_order_by_id(self, order_id: int):
        # Get order with order details from our own database
        order_query = (
            self.db.query(
                Orders.id,
                Orders.order_date,
                Orders.status,
                Orders.customer_id,
                Orders.product_id,
                OrderDetails.quantity,
            )
            .join(OrderDetails, Orders.id == OrderDetails.order_id)
            .filter(Orders.id == order_id)
            .first()
        )

        if order_query is None:
            raise HTTPException(status_code=404, detail="Order not found")

        # Enrich with product and customer data
        product_info = await self.get_product_info(order_query.product_id)
        customer_info = await self.get_customer_info(order_query.customer_id)
        
        return {
            "id": order_query.id,
            "order_date": order_query.order_date,
            "status": order_query.status,
            "customer_id": order_query.customer_id,
            "product_id": order_query.product_id,
            "product_name": product_info.get("name") if product_info else "Unknown Product",
            "customer_name": customer_info.get("name") if customer_info else "Unknown Customer",
            "quantity": order_query.quantity,
        }
        
    async def order_create(self, order_data: OrderCreate):
        # Get product info to calculate total
        product_info = await self.get_product_info(order_data.product_id)
        if not product_info:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Verify customer exists
        customer_info = await self.get_customer_info(order_data.customer_id)
        if not customer_info:
            raise HTTPException(status_code=404, detail="Customer not found")
        
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
        total_amount = product_info["price"] * order_data.quantity
        
        # Create order details
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