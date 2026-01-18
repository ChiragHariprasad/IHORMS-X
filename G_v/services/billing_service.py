"""
Billing Service - Handles billing and finance operations
"""
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from decimal import Decimal

from models import Billing, Appointment, Patient, InsuranceClaim, ClaimStatus
from schemas.billing import BillingCreate, PaymentUpdate
from utils.exceptions import NotFoundError, ValidationError
from utils.audit import audit_logger


class BillingService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_billing_by_id(self, billing_id: int) -> Optional[Billing]:
        return self.db.query(Billing).filter(Billing.id == billing_id).first()
    
    def generate_bill(
        self, 
        data: BillingCreate, 
        created_by: int
    ) -> Billing:
        """Generate a bill for an appointment"""
        appointment = self.db.query(Appointment).filter(Appointment.id == data.appointment_id).first()
        if not appointment:
            raise NotFoundError("Appointment", str(data.appointment_id))
        
        # Check if bill already exists
        existing = self.db.query(Billing).filter(Billing.appointment_id == data.appointment_id).first()
        if existing:
            return existing
        
        patient = self.db.query(Patient).filter(Patient.id == appointment.patient_id).first()
        
        # Calculate totals
        subtotal = (data.consultation_fee + data.medication_cost + 
                   data.room_charges + data.test_charges + data.other_charges)
        tax = subtotal * Decimal('0.05')  # 5% tax
        total_amount = subtotal + tax - data.discount
        
        # Generate bill number
        bill_count = self.db.query(Billing).count()
        bill_number = f"BILL-{datetime.now().year}-{bill_count + 1:06d}"
        
        bill = Billing(
            appointment_id=data.appointment_id,
            patient_id=appointment.patient_id,
            bill_number=bill_number,
            bill_date=datetime.utcnow(),
            consultation_fee=data.consultation_fee,
            medication_cost=data.medication_cost,
            room_charges=data.room_charges,
            test_charges=data.test_charges,
            other_charges=data.other_charges,
            subtotal=subtotal,
            tax=tax,
            discount=data.discount,
            total_amount=total_amount,
            amount_paid=Decimal(0),
            payment_status='pending',
            payment_method=data.payment_method
        )
        self.db.add(bill)
        
        audit_logger.log_action(
            self.db, created_by, "BILL_GENERATED", "Billing", bill.id,
            after_state={"bill_number": bill_number, "total": float(total_amount)}
        )
        
        self.db.commit()
        return bill
    
    def update_payment(
        self, 
        billing_id: int, 
        data: PaymentUpdate, 
        updated_by: int
    ) -> Billing:
        """Update payment for a bill"""
        bill = self.get_billing_by_id(billing_id)
        if not bill:
            raise NotFoundError("Billing", str(billing_id))
        
        bill.amount_paid += data.amount_paid
        bill.payment_method = data.payment_method
        
        if bill.amount_paid >= bill.total_amount:
            bill.payment_status = 'paid'
        elif bill.amount_paid > 0:
            bill.payment_status = 'partial'
            
        audit_logger.log_action(
            self.db, updated_by, "PAYMENT_UPDATED", "Billing", bill.id,
            after_state={"amount_paid": float(data.amount_paid), "status": bill.payment_status}
        )
        
        self.db.commit()
        return bill
    
    def get_patient_billing_history(self, patient_id: int) -> List[Billing]:
        """Get billing history for a patient"""
        return self.db.query(Billing).filter(
            Billing.patient_id == patient_id
        ).order_by(Billing.bill_date.desc()).all()
    
    def get_branch_revenue(self, branch_id: int, from_date: datetime, to_date: datetime) -> Decimal:
        """Calculate total revenue for a branch"""
        result = self.db.query(func.sum(Billing.amount_paid)).join(
            Patient
        ).filter(
            Patient.branch_id == branch_id,
            Billing.bill_date >= from_date,
            Billing.bill_date <= to_date
        ).scalar()
        
        return result or Decimal(0)
