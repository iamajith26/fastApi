from fastapi import APIRouter, Depends, HTTPException
from app.db.session import get_db
from app.schemas.orders import OrderCreate, OrderUpdate, OrderOut
from app.services.order_service import OrderService, get_order_service
from app.schemas.orders import OrderUpdateTotal
from sqlalchemy import text

router = APIRouter()

@router.get('/', response_model=list[OrderOut])
def list_orders(
    order_service: OrderService = Depends(get_order_service),
):
    orders = order_service.get_all_orders()
    if not orders:
        raise HTTPException(status_code=404, detail="No orders found")
    return orders

@router.get('/{order_id}', response_model=OrderOut)
def read_order(
    order_id: int,
    order_service: OrderService = Depends(get_order_service),
):
    order = order_service.get_order_by_id(order_id)
    return order

# Not working need to check
@router.post("/update_total")
async def update_order_total(payload: OrderUpdateTotal, db=Depends(get_db)):
    await db.execute(
        text('CALL order_procedure(:amount, :o_id)'),
        {"amount": payload.amount, "o_id": payload.o_id}
    )
    return {"status": "success", "o_id": payload.o_id}