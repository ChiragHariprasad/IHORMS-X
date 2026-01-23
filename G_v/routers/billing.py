"""
Billing Router
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from database import get_db
from models import User, UserRole
from schemas.billing import BillingCreate, BillingResponse, PaymentUpdate
from services.billing_service import BillingService
from auth.dependencies import get_current_user, require_roles

router = APIRouter(prefix="/billing", tags=["Billing & Finance"])

@router.post("/", response_model=BillingResponse)
def create_bill(
    data: BillingCreate, 
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    service = BillingService(db)
    return service.generate_bill(data, user.id)

@router.get("/patient/{patient_id}", response_model=List[BillingResponse])
def get_patient_bills(
    patient_id: int, 
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    service = BillingService(db)
    return service.get_patient_billing_history(patient_id)

@router.post("/{billing_id}/payment", response_model=BillingResponse)
def update_payment(
    billing_id: int, 
    data: PaymentUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    service = BillingService(db)
    return service.update_payment(billing_id, data, user.id)

@router.get("/my-bills", response_model=List[BillingResponse])
def get_my_bills(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Patient can view their own bills"""
    if user.role != UserRole.PATIENT:
        raise HTTPException(status_code=403, detail="Only patients can access this")
    
    from models import Patient
    patient = db.query(Patient).filter(Patient.user_id == user.id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found")
    
    service = BillingService(db)
    return service.get_patient_billing_history(patient.id)

@router.post("/my-bills/{billing_id}/pay", response_model=BillingResponse)
def pay_my_bill(
    billing_id: int,
    payment_method: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Patient pays their own bill"""
    if user.role != UserRole.PATIENT:
        raise HTTPException(status_code=403, detail="Only patients can pay")
    
    from models import Patient
    patient = db.query(Patient).filter(Patient.user_id == user.id).first()
    service = BillingService(db)
    
    bill = service.get_billing_by_id(billing_id)
    if not bill or bill.patient_id != patient.id:
        raise HTTPException(status_code=404, detail="Bill not found")
    
    remaining = bill.total_amount - bill.amount_paid
    payment_data = PaymentUpdate(amount_paid=remaining, payment_method=payment_method)
    return service.update_payment(billing_id, payment_data, user.id)

@router.post("/my-bills/{billing_id}/insurance", response_model=BillingResponse)
def claim_insurance(
    billing_id: int,
    insurance_provider: str,
    policy_number: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Patient claims insurance for their bill"""
    if user.role != UserRole.PATIENT:
        raise HTTPException(status_code=403, detail="Only patients can claim")
    
    from models import Patient, InsuranceClaim, ClaimStatus
    patient = db.query(Patient).filter(Patient.user_id == user.id).first()
    service = BillingService(db)
    
    bill = service.get_billing_by_id(billing_id)
    if not bill or bill.patient_id != patient.id:
        raise HTTPException(status_code=404, detail="Bill not found")
    
    # Create insurance claim
    claim = InsuranceClaim(
        billing_id=billing_id,
        patient_id=patient.id,
        insurance_provider=insurance_provider,
        policy_number=policy_number,
        claimed_amount=bill.total_amount - bill.amount_paid,
        claim_number=f"CLM-{datetime.now().year}-{db.query(InsuranceClaim).count() + 1:06d}",
        status=ClaimStatus.SUBMITTED,
        submitted_date=datetime.utcnow()
    )
    db.add(claim)
    
    bill.payment_status = 'insurance_pending'
    db.commit()
    return bill

@router.post("/discharge/request")
def request_discharge(
    admission_id: int,
    discharge_notes: str = "",
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Nurse requests patient discharge"""
    if user.role != UserRole.NURSE:
        raise HTTPException(status_code=403, detail="Only nurses can request discharge")
    
    from models import Admission, AdmissionStatus
    admission = db.query(Admission).filter(Admission.id == admission_id).first()
    if not admission:
        raise HTTPException(status_code=404, detail="Admission not found")
    
    admission.discharge_requested = True
    admission.discharge_requested_by = user.id
    admission.discharge_request_notes = discharge_notes
    admission.discharge_request_date = datetime.utcnow()
    db.commit()
    
    return {"status": "success", "message": "Discharge request sent to doctor"}

@router.post("/discharge/approve/{admission_id}")
def approve_discharge(
    admission_id: int,
    approved: bool,
    discharge_summary: str = "",
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Doctor approves/rejects discharge"""
    if user.role != UserRole.DOCTOR:
        raise HTTPException(status_code=403, detail="Only doctors can approve discharge")
    
    from models import Admission, AdmissionStatus, Room
    admission = db.query(Admission).filter(Admission.id == admission_id).first()
    if not admission:
        raise HTTPException(status_code=404, detail="Admission not found")
    
    if admission.admitted_by != user.id:
        raise HTTPException(status_code=403, detail="Only the admitting doctor can approve discharge")
    
    if approved:
        admission.status = AdmissionStatus.DISCHARGED
        admission.discharge_date = datetime.utcnow()
        admission.discharge_summary = discharge_summary
        admission.discharge_approved_by = user.id
        
        # Free up the room
        if admission.room_id:
            room = db.query(Room).filter(Room.id == admission.room_id).first()
            if room:
                room.is_available = True
                room.current_patient_id = None
        
        db.commit()
        return {"status": "success", "message": "Patient discharged successfully"}
    else:
        admission.discharge_requested = False
        admission.discharge_request_notes = None
        db.commit()
        return {"status": "success", "message": "Discharge request rejected"}
