"""
Nurse Router
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import User
from schemas.clinical import TelemetryCreate, TelemetryResponse, RoomResponse, AdmissionResponse
from schemas.appointment import AppointmentResponse
from services.clinical_service import ClinicalService
from services.appointment_service import AppointmentService
from auth.dependencies import get_nurse

router = APIRouter(prefix="/nurse", tags=["Nurse"])

@router.get("/appointments", response_model=List[AppointmentResponse])
def view_branch_appointments(
    db: Session = Depends(get_db),
    nurse: User = Depends(get_nurse)
):
    service = AppointmentService(db)
    apps, _ = service.get_branch_appointments(nurse.branch_id)
    return apps

@router.post("/telemetry", response_model=TelemetryResponse)
def record_vitals(
    data: TelemetryCreate, 
    db: Session = Depends(get_db),
    nurse: User = Depends(get_nurse)
):
    service = ClinicalService(db)
    return service.add_telemetry(data, nurse.id)

@router.get("/telemetry/active-alerts")
def get_alerts(
    db: Session = Depends(get_db),
    nurse: User = Depends(get_nurse)
):
    # This would involve a websocket or polling in a real app
    # For now, just a basic filter
    from models import TelemetryData
    return db.query(TelemetryData).filter(TelemetryData.alert_triggered == True).all()

@router.get("/rooms", response_model=List[RoomResponse])
def list_ward_rooms(
    db: Session = Depends(get_db),
    nurse: User = Depends(get_nurse)
):
    from models import Room, Appointment, AppointmentStatus
    rooms = db.query(Room).filter(Room.branch_id == nurse.branch_id).all()
    
    # Populate occupant info dynamically
    for room in rooms:
        active_admission = db.query(Appointment).filter(
            Appointment.room_id == room.id,
            Appointment.status == AppointmentStatus.ADMITTED
        ).first()
        
        if active_admission:
            # We assign these attributes dynamically to the ORM object (Pydantic will pick them up)
            # This works because python objects are dynamic, but cleaner would be converting to dict.
            # However, simpler for now:
            setattr(room, "occupant_name", active_admission.patient_name)
            setattr(room, "appointment_id", active_admission.id)
            
    return rooms

@router.get("/admissions", response_model=List[AdmissionResponse])
def get_admitted_patients(
    db: Session = Depends(get_db),
    nurse: User = Depends(get_nurse)
):
    from models import Admission, AdmissionStatus, Patient
    # Get admissions for patients in the nurse's branch
    return db.query(Admission).join(Patient).filter(
        Patient.branch_id == nurse.branch_id,
        Admission.status == AdmissionStatus.ADMITTED
    ).all()
