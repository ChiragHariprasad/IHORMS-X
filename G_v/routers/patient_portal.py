"""
Patient Portal Router
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import date, time

from database import get_db
from models import User, Patient
from schemas.appointment import AppointmentResponse
from schemas.clinical import MedicalHistoryResponse
from services.appointment_service import AppointmentService
from services.patient_service import PatientService
from auth.dependencies import get_patient_user

router = APIRouter(prefix="/patient-portal", tags=["Patient Portal"])

@router.get("/profile")
async def get_my_profile(
    db: Session = Depends(get_db),
    user: User = Depends(get_patient_user)
):
    service = PatientService(db)
    patient = service.get_patient_by_user_id(user.id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found")
    
    return {
        "id": patient.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "phone": user.phone,
        "patient_uid": patient.patient_uid,
        "blood_group": patient.blood_group
    }

@router.get("/history")
async def get_my_medical_history(
    db: Session = Depends(get_db),
    user: User = Depends(get_patient_user)
):
    service = PatientService(db)
    patient = service.get_patient_by_user_id(user.id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found")
    
    records = service.get_patient_medical_history(patient.id, user.id, "Self access")
    return {"records": records}

@router.get("/doctors")
async def list_available_doctors(
    db: Session = Depends(get_db),
    user: User = Depends(get_patient_user)
):
    from models import UserRole, Doctor
    doctors = db.query(User, Doctor).join(Doctor, User.id == Doctor.user_id).filter(User.role == UserRole.DOCTOR).all()
    return [
        {
            "id": u.id,
            "first_name": u.first_name,
            "last_name": u.last_name,
            "specialization": d.specialization
        } for u, d in doctors
    ]

@router.get("/appointments", response_model=List[AppointmentResponse])
async def list_my_appointments(
    db: Session = Depends(get_db),
    user: User = Depends(get_patient_user)
):
    ps = PatientService(db)
    patient = ps.get_patient_by_user_id(user.id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found")
        
    service = AppointmentService(db)
    apps, _ = service.get_patient_appointments(patient.id)
    return apps

@router.post("/appointments/book")
async def book_appointment(
    doctor_id: int,
    appointment_date: date,
    appointment_time: time,
    chief_complaint: str = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_patient_user)
):
    service = AppointmentService(db)
    return service.book_appointment_by_patient(
        user.id, doctor_id, appointment_date, appointment_time, chief_complaint
    )
