"""
Inventory and Pharmacy Schemas
"""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from decimal import Decimal


class InventoryBase(BaseModel):
    medicine_name: str
    generic_name: Optional[str] = None
    manufacturer: Optional[str] = None
    batch_number: Optional[str] = None
    quantity: int
    unit_price: Decimal
    expiry_date: Optional[date] = None
    reorder_level: int = 50


class InventoryCreate(InventoryBase):
    pass


class InventoryUpdate(BaseModel):
    quantity: Optional[int] = None
    unit_price: Optional[Decimal] = None
    reorder_level: Optional[int] = None


class InventoryRestock(BaseModel):
    quantity: int


class InventoryResponse(InventoryBase):
    id: int
    branch_id: int
    last_restocked: Optional[datetime]
    is_low_stock: bool
    is_expired: bool
    
    class Config:
        from_attributes = True


class InventoryListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[InventoryResponse]
    low_stock_count: int
    expired_count: int


class PharmacyOrderCreate(BaseModel):
    patient_id: int
    items: List[Dict[str, Any]]  # [{"medicine_name": "x", "quantity": 2}]


class PharmacyOrderResponse(BaseModel):
    id: int
    order_number: str
    patient_id: int
    patient_name: str
    order_date: datetime
    items: Dict[str, Any]
    total_amount: Decimal
    status: str
    fulfilled_date: Optional[datetime]
    fulfilled_by: Optional[str]
    
    class Config:
        from_attributes = True


class PharmacyOrderListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[PharmacyOrderResponse]


class InventoryAnalytics(BaseModel):
    total_items: int
    total_value: Decimal
    low_stock_items: int
    expired_items: int
    expiring_soon: int
    top_moving_items: List[dict]
    reorder_required: List[dict]
