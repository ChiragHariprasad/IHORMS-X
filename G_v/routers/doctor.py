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
from services.appointment_service import AppointmentService
from services.patient_service import PatientService
from auth.dependencies import get_doctor

router = APIRouter(prefix="/doctor", tags=["Doctor"])

@router.get("/appointments", response_model=List[AppointmentResponse])
async def list_assigned_appointments(
    db: Session = Depends(get_db),
    doctor: User = Depends(get_doctor)
):
    service = AppointmentService(db)
    apps, _ = service.get_doctor_appointments(doctor.id)
    return apps

@router.get("/schedule", response_model=List[AppointmentResponse])
async def get_schedule(
    schedule_date: date = date.today(),
    db: Session = Depends(get_db),
    doctor: User = Depends(get_doctor)
):
    service = AppointmentService(db)
    return service.get_doctor_schedule(doctor.id, schedule_date)

@router.post("/appointments/{app_id}/accept")
async def accept_appointment(
    app_id: int, 
    db: Session = Depends(get_db),
    doctor: User = Depends(get_doctor)
):
    service = AppointmentService(db)
    return service.accept_appointment(app_id, doctor.id)

@router.post("/appointments/{app_id}/notes")
async def add_clinical_notes(
    app_id: int, 
    data: DoctorNotesUpdate,
    db: Session = Depends(get_db),
    doctor: User = Depends(get_doctor)
):
    service = AppointmentService(db)
    return service.add_doctor_notes(app_id, doctor.id, data)

@router.get("/patients/{patient_id}/history", response_model=List[MedicalHistoryResponse])
async def view_patient_history(
    patient_id: int, 
    reason: str = "Clinical review",
    db: Session = Depends(get_db),
    doctor: User = Depends(get_doctor)
):
    service = PatientService(db)
    return service.get_patient_medical_history(patient_id, doctor.id, reason)

@router.get("/patients/search")
async def find_patient_by_uid(
    uid: str, 
    db: Session = Depends(get_db),
    doctor: User = Depends(get_doctor)
):
    service = PatientService(db)
    patient = service.get_patient_by_uid(uid)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient
