"""
Billing Schemas
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class BillingCreate(BaseModel):
    appointment_id: int
    consultation_fee: Decimal
    medication_cost: Decimal = Decimal(0)
    room_charges: Decimal = Decimal(0)
    test_charges: Decimal = Decimal(0)
    other_charges: Decimal = Decimal(0)
    discount: Decimal = Decimal(0)
    payment_method: Optional[str] = None


class BillingResponse(BaseModel):
    id: int
    bill_number: str
    appointment_id: int
    patient_id: int
    patient_name: str
    bill_date: datetime
    consultation_fee: Decimal
    medication_cost: Decimal
    room_charges: Decimal
    test_charges: Decimal
    other_charges: Decimal
    subtotal: Decimal
    tax: Decimal
    discount: Decimal
    total_amount: Decimal
    amount_paid: Decimal
    payment_status: str
    payment_method: Optional[str]
    
    class Config:
        from_attributes = True


class PaymentUpdate(BaseModel):
    amount_paid: Decimal
    payment_method: str


class InsuranceClaimResponse(BaseModel):
    id: int
    claim_number: str
    billing_id: int
    patient_id: int
    insurance_provider: str
    policy_number: str
    claimed_amount: Decimal
    approved_amount: Optional[Decimal]
    status: str
    submitted_date: datetime
    processed_date: Optional[datetime]
    
    class Config:
        from_attributes = True
