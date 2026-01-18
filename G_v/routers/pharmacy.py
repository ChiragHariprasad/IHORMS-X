"""
Pharmacy Router
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from database import get_db
from models import User, PharmacyOrder, OrderStatus
from schemas.inventory import (
    InventoryResponse, InventoryCreate, 
    PharmacyOrderCreate, PharmacyOrderResponse
)
from services.inventory_service import InventoryService
from auth.dependencies import get_pharmacy_staff

router = APIRouter(prefix="/pharmacy", tags=["Pharmacy"])

@router.get("/inventory", response_model=List[InventoryResponse])
async def list_stock(
    low_stock: bool = False,
    db: Session = Depends(get_db),
    staff: User = Depends(get_pharmacy_staff)
):
    service = InventoryService(db)
    items, _ = service.get_inventory_by_branch(staff.branch_id, low_stock_only=low_stock)
    return items

@router.post("/inventory", response_model=InventoryResponse)
async def add_stock(
    data: InventoryCreate, 
    db: Session = Depends(get_db),
    staff: User = Depends(get_pharmacy_staff)
):
    service = InventoryService(db)
    return service.add_inventory_item(staff.branch_id, data, staff.id)

@router.post("/inventory/{item_id}/restock", response_model=InventoryResponse)
async def restock_item(
    item_id: int,
    quantity: int,
    db: Session = Depends(get_db),
    staff: User = Depends(get_pharmacy_staff)
):
    service = InventoryService(db)
    return service.restock_item(item_id, quantity, staff.id)

@router.post("/orders", response_model=PharmacyOrderResponse)
async def fulfill_prescription(
    data: PharmacyOrderCreate, 
    db: Session = Depends(get_db),
    staff: User = Depends(get_pharmacy_staff)
):
    service = InventoryService(db)
    return service.create_order(staff.branch_id, data, staff.id)

@router.get("/orders/pending", response_model=List[PharmacyOrderResponse])
async def list_pending_orders(
    db: Session = Depends(get_db),
    staff: User = Depends(get_pharmacy_staff)
):
    return db.query(PharmacyOrder).filter(
        PharmacyOrder.status == OrderStatus.PENDING
    ).all()

@router.post("/orders/{order_id}/fulfill", response_model=PharmacyOrderResponse)
async def fulfill_order(
    order_id: int,
    db: Session = Depends(get_db),
    staff: User = Depends(get_pharmacy_staff)
):
    order = db.query(PharmacyOrder).filter(PharmacyOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order.status = OrderStatus.FULFILLED
    order.fulfilled_date = datetime.utcnow()
    order.pharmacy_staff_id = staff.id
    db.commit()
    return order
