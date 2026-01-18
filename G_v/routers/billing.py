"""
Billing Router
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import User, UserRole
from schemas.billing import BillingCreate, BillingResponse, PaymentUpdate
from services.billing_service import BillingService
from auth.dependencies import get_current_user, require_roles

router = APIRouter(prefix="/billing", tags=["Billing & Finance"])

@router.post("/", response_model=BillingResponse)
async def create_bill(
    data: BillingCreate, 
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    service = BillingService(db)
    return service.generate_bill(data, user.id)

@router.get("/patient/{patient_id}", response_model=List[BillingResponse])
async def get_patient_bills(
    patient_id: int, 
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    service = BillingService(db)
    return service.get_patient_billing_history(patient_id)

@router.post("/{billing_id}/payment", response_model=BillingResponse)
async def update_payment(
    billing_id: int, 
    data: PaymentUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    service = BillingService(db)
    return service.update_payment(billing_id, data, user.id)
