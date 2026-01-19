from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.db.session import get_db
from sqlalchemy.orm import Session
from orders_service.services.order_service import get_order_service, OrderService
from orders_service.schemas.orders import OrderCreate, OrderUpdateTotal, OrderOut
from sqlalchemy import text
from typing import Optional, List
import logging
import os

app = FastAPI(
    title="Orders Microservice",
    description="Microservice for order management",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

logger = logging.getLogger(__name__)



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def validate_gateway_request(
    x_user_id: Optional[str] = Header(None)
):
    """Validate that request comes from authenticated gateway"""
    # Allow direct access for testing/development
    if os.getenv("ALLOW_DIRECT_ACCESS", "false").lower() == "true":
        if not x_user_id:
            logger.warning("Direct access allowed - no gateway headers found")
            return {"user_id": 1}
    
    # Production mode - require gateway headers
    if not x_user_id:
        raise HTTPException(
            status_code=401,
            detail="Request must come from authenticated gateway"
        )
    
    logger.info(f"Orders request from user ID: {x_user_id}")
    return {"user_id": int(x_user_id)}

def get_order_service_with_user(
    user_context: dict = Depends(validate_gateway_request),
    db: Session = Depends(get_db)
) -> OrderService:
    """Get OrderService with user context"""
    user_id = str(user_context.get("user_id"))
    return OrderService(db, user_id=user_id)

# Orders Routes - moved from main app
@app.get("/orders/", response_model=List[OrderOut])
async def get_orders(
    user_context: dict = Depends(validate_gateway_request),
    order_service: OrderService = Depends(get_order_service_with_user)
):
    """Get all orders with customer and product details"""
    orders = await order_service.get_all_orders()
    if not orders:
        raise HTTPException(status_code=404, detail="No orders found")
    return orders

@app.post("/orders/create_order")
async def create_order(
    order_data: OrderCreate,
    user_context: dict = Depends(validate_gateway_request),
    order_service: OrderService = Depends(get_order_service_with_user)
):
    """Create a new order with order details"""
    new_order = await order_service.order_create(order_data)
    return {"status": "success", "order_id": new_order.id}

@app.get("/orders/{order_id}", response_model=OrderOut)
async def get_order(
    order_id: int,
    user_context: dict = Depends(validate_gateway_request),
    order_service: OrderService = Depends(get_order_service_with_user)
):
    """Get a specific order by ID with customer and product details"""
    order = await order_service.get_order_by_id(order_id)
    return order

@app.post("/orders/update_total")
async def update_order_total(
    payload: OrderUpdateTotal,
    user_context: dict = Depends(validate_gateway_request),
    db=Depends(get_db)
):
    """Update order total using stored procedure"""
    await db.execute(
        text('CALL order_procedure(:amount, :o_id)'),
        {"amount": payload.amount, "o_id": payload.o_id}
    )
    return {"status": "success", "o_id": payload.o_id}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "orders"}