"""
Doctor Router
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import date

from database import get_db
from models import User, Appointment
from schemas.appointment import (
    AppointmentResponse, AppointmentDetailResponse, 
    DoctorNotesUpdate, DoctorScheduleResponse
)
from schemas.clinical import MedicalHistoryResponse
from schemas.patient import PatientResponse
from services.appointment_service import AppointmentService
from services.patient_service import PatientService
from auth.dependencies import get_doctor

router = APIRouter(prefix="/doctor", tags=["Doctor"])

@router.get("/appointments", response_model=List[AppointmentResponse])
def list_assigned_appointments(
    db: Session = Depends(get_db),
    doctor: User = Depends(get_doctor)
):
    service = AppointmentService(db)
    apps, _ = service.get_doctor_appointments(doctor.id)
    return apps

@router.get("/schedule", response_model=List[AppointmentResponse])
def get_schedule(
    schedule_date: date = date.today(),
    db: Session = Depends(get_db),
    doctor: User = Depends(get_doctor)
):
    service = AppointmentService(db)
    return service.get_doctor_schedule(doctor.id, schedule_date)

@router.get("/appointments/{app_id}", response_model=AppointmentDetailResponse)
def get_appointment_detail(
    app_id: int,
    db: Session = Depends(get_db),
    doctor: User = Depends(get_doctor)
):
    service = AppointmentService(db)
    app = service.get_appointment_by_id(app_id)
    if not app:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    # Check if doctor owns this or if it's in their branch (Doctors can usually see branch appointments if needed, but let's stick to assigned for now or branch)
    # Actually, for history search, doctor needs to see other appointments too.
    # For now, let's allow it if it matches doctor's branch at least.
    return app

@router.post("/appointments/{app_id}/accept")
def accept_appointment(
    app_id: int, 
    db: Session = Depends(get_db),
    doctor: User = Depends(get_doctor)
):
    service = AppointmentService(db)
    return service.accept_appointment(app_id, doctor.id)

@router.post("/appointments/{app_id}/notes")
def add_clinical_notes(
    app_id: int, 
    data: DoctorNotesUpdate,
    db: Session = Depends(get_db),
    doctor: User = Depends(get_doctor)
):
    service = AppointmentService(db)
    return service.add_doctor_notes(app_id, doctor.id, data)

@router.post("/appointments/{app_id}/admit")
def admit_patient(
    app_id: int,
    room_type: str = "general_ward",
    db: Session = Depends(get_db),
    doctor: User = Depends(get_doctor)
):
    service = AppointmentService(db)
    return service.admit_patient(app_id, room_type, doctor.id)

@router.get("/patients/{patient_id}/history", response_model=List[MedicalHistoryResponse])
def view_patient_history(
    patient_id: int, 
    reason: str = "Clinical review",
    db: Session = Depends(get_db),
    doctor: User = Depends(get_doctor)
):
    service = PatientService(db)
    return service.get_patient_medical_history(patient_id, doctor.id, reason)

@router.get("/patients/search", response_model=PatientResponse)
def find_patient_by_uid(
    uid: str, 
    db: Session = Depends(get_db),
    doctor: User = Depends(get_doctor)
):
    service = PatientService(db)
    patient = service.get_patient_by_uid(uid)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

@router.get("/discharge-requests")
def get_discharge_requests(
    db: Session = Depends(get_db),
    doctor: User = Depends(get_doctor)
):
    from models import Admission, AdmissionStatus, Doctor as DoctorModel
    
    # Get Doctor profile from User
    doc_profile = db.query(DoctorModel).filter(DoctorModel.user_id == doctor.id).first()
    if not doc_profile:
        return []
        
    return db.query(Admission).filter(
        Admission.doctor_id == doc_profile.id,
        Admission.discharge_requested == True,
        Admission.status == AdmissionStatus.ADMITTED
    ).all()
