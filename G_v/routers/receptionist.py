"""
Receptionist Router
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import User
from schemas.patient import PatientCreate, PatientResponse, PatientSearchResult
from schemas.appointment import AppointmentCreate, AppointmentResponse, AppointmentReschedule
from services.patient_service import PatientService
from services.appointment_service import AppointmentService
from datetime import date
from auth.dependencies import get_receptionist

router = APIRouter(prefix="/receptionist", tags=["Receptionist"])

@router.get("/appointments", response_model=List[AppointmentResponse])
def list_appointments(
    date: str = date.today().isoformat(),
    db: Session = Depends(get_db),
    staff: User = Depends(get_receptionist)
):
    service = AppointmentService(db)
    apps, _ = service.get_branch_appointments(staff.branch_id)
    return [a for a in apps if str(a.appointment_date) == date]

@router.get("/doctors")
def list_branch_doctors(
    db: Session = Depends(get_db),
    staff: User = Depends(get_receptionist)
):
    from services.user_service import UserService
    from models import UserRole
    service = UserService(db)
    doctors, _ = service.get_staff_by_branch(staff.branch_id, role=UserRole.DOCTOR)
    return doctors

@router.get("/doctors/recommend")
def recommend_doctors_for_symptoms(
    symptoms: str,
    db: Session = Depends(get_db),
    staff: User = Depends(get_receptionist)
):
    """Get AI-recommended doctors based on patient symptoms"""
    from services.doctor_recommendation_service import DoctorRecommendationService
    
    service = DoctorRecommendationService(db)
    recommendations = service.recommend_doctors(symptoms, staff.branch_id, limit=10)
    
    return [
        {
            **doctor,
            "confidence": round(score * 100, 1),
            "reason": f"Match based on {doctor['specialization']}"
        }
        for doctor, score in recommendations
    ]

@router.post("/patients", response_model=PatientResponse)
def register_patient(
    data: PatientCreate, 
    db: Session = Depends(get_db),
    staff: User = Depends(get_receptionist)
):
    service = PatientService(db)
    return service.create_patient(data, staff.organization_id, staff.branch_id, staff.id)

@router.get("/patients/search", response_model=PatientSearchResult)
def search_patients(
    query: str = None, 
    page: int = 1,
    db: Session = Depends(get_db),
    staff: User = Depends(get_receptionist)
):
    service = PatientService(db)
    items, total = service.search_patients(staff.branch_id, query, page)
    return {"items": items, "total": total, "page": page, "page_size": 20}

@router.post("/appointments", response_model=AppointmentResponse)
def schedule_appointment(
    data: AppointmentCreate, 
    db: Session = Depends(get_db),
    staff: User = Depends(get_receptionist)
):
    service = AppointmentService(db)
    return service.create_appointment(data, staff.branch_id, staff.id)

@router.post("/appointments/{app_id}/reschedule")
def reschedule(
    app_id: int, 
    data: AppointmentReschedule,
    db: Session = Depends(get_db),
    staff: User = Depends(get_receptionist)
):
    service = AppointmentService(db)
    return service.reschedule_appointment(app_id, data, staff.id)

@router.post("/appointments/{app_id}/confirm")
def confirm_appointment(
    app_id: int,
    db: Session = Depends(get_db),
    staff: User = Depends(get_receptionist)
):
    service = AppointmentService(db)
    return service.confirm_appointment(app_id, staff.id)
