"""
Inventory Service - Handles pharmacy and inventory operations
"""
from typing import Optional, List, Tuple, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, date, timedelta
from decimal import Decimal

from models import Inventory, PharmacyOrder, OrderStatus, Patient, User
from schemas.inventory import (
    InventoryCreate, InventoryUpdate, InventoryRestock, 
    PharmacyOrderCreate
)
from utils.exceptions import NotFoundError, ValidationError, ConflictError
from utils.audit import audit_logger


class InventoryService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_inventory_item(self, item_id: int) -> Optional[Inventory]:
        return self.db.query(Inventory).filter(Inventory.id == item_id).first()
    
    def get_inventory_by_branch(
        self, 
        branch_id: int,
        low_stock_only: bool = False,
        expired_only: bool = False,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[Inventory], int]:
        """Get inventory items for a branch"""
        query = self.db.query(Inventory).filter(Inventory.branch_id == branch_id)
        
        if low_stock_only:
            query = query.filter(Inventory.quantity <= Inventory.reorder_level)
        if expired_only:
            query = query.filter(Inventory.expiry_date <= date.today())
        if search:
            query = query.filter(Inventory.medicine_name.ilike(f"%{search}%"))
            
        total = query.count()
        items = query.offset((page - 1) * page_size).limit(page_size).all()
        
        return items, total
    
    def add_inventory_item(self, branch_id: int, data: InventoryCreate, created_by: int) -> Inventory:
        """Add new medicine to inventory"""
        item = Inventory(
            branch_id=branch_id,
            medicine_name=data.medicine_name,
            generic_name=data.generic_name,
            manufacturer=data.manufacturer,
            batch_number=data.batch_number,
            quantity=data.quantity,
            unit_price=data.unit_price,
            expiry_date=data.expiry_date,
            reorder_level=data.reorder_level,
            last_restocked=datetime.utcnow()
        )
        self.db.add(item)
        self.db.commit()
        return item
    
    def restock_item(self, item_id: int, quantity: int, updated_by: int) -> Inventory:
        """Restock an existing item"""
        item = self.get_inventory_item(item_id)
        if not item:
            raise NotFoundError("Inventory item", str(item_id))
            
        item.quantity += quantity
        item.last_restocked = datetime.utcnow()
        
        audit_logger.log_action(
            self.db, updated_by, "INVENTORY_RESTOCKED", "Inventory", item_id,
            after_state={"added": quantity, "new_total": item.quantity}
        )
        
        self.db.commit()
        return item
    
    def create_order(self, branch_id: int, data: PharmacyOrderCreate, staff_user_id: int) -> PharmacyOrder:
        """Create and fulfill a pharmacy order"""
        # Calculate total and check stock
        total_amount = Decimal(0)
        items_detail = []
        
        for item in data.items:
            inventory = self.db.query(Inventory).filter(
                Inventory.branch_id == branch_id,
                Inventory.medicine_name == item['medicine_name']
            ).first()
            
            if not inventory:
                raise NotFoundError(f"Medicine: {item['medicine_name']}")
            
            if inventory.quantity < item['quantity']:
                raise ValidationError(f"Insufficient stock for {item['medicine_name']}")
            
            # Deduct stock
            inventory.quantity -= item['quantity']
            
            price = inventory.unit_price * item['quantity']
            total_amount += price
            items_detail.append({
                "medicine_name": item['medicine_name'],
                "quantity": item['quantity'],
                "price": float(price)
            })
            
        order_count = self.db.query(PharmacyOrder).count()
        order_number = f"ORD-{datetime.now().year}-{order_count + 1:06d}"
        
        order = PharmacyOrder(
            patient_id=data.patient_id,
            pharmacy_staff_id=staff_user_id,
            order_number=order_number,
            order_date=datetime.utcnow(),
            items=items_detail,
            total_amount=total_amount,
            status=OrderStatus.FULFILLED,
            fulfilled_date=datetime.utcnow()
        )
        self.db.add(order)
        
        audit_logger.log_action(
            self.db, staff_user_id, "PHARMACY_ORDER_FULFILLED", "PharmacyOrder", order.id,
            after_state={"total": float(total_amount)}
        )
        
        self.db.commit()
        return order
