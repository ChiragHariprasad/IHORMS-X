"""
Nurse Router
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import User
from schemas.clinical import TelemetryCreate, TelemetryResponse
from schemas.appointment import AppointmentResponse
from services.clinical_service import ClinicalService
from services.appointment_service import AppointmentService
from auth.dependencies import get_nurse

router = APIRouter(prefix="/nurse", tags=["Nurse"])

@router.get("/appointments", response_model=List[AppointmentResponse])
async def view_branch_appointments(
    db: Session = Depends(get_db),
    nurse: User = Depends(get_nurse)
):
    service = AppointmentService(db)
    apps, _ = service.get_branch_appointments(nurse.branch_id)
    return apps

@router.post("/telemetry", response_model=TelemetryResponse)
async def record_vitals(
    data: TelemetryCreate, 
    db: Session = Depends(get_db),
    nurse: User = Depends(get_nurse)
):
    service = ClinicalService(db)
    return service.add_telemetry(data, nurse.id)

@router.get("/telemetry/active-alerts")
async def get_alerts(
    db: Session = Depends(get_db),
    nurse: User = Depends(get_nurse)
):
    # This would involve a websocket or polling in a real app
    # For now, just a basic filter
    from models import TelemetryData
    return db.query(TelemetryData).filter(TelemetryData.alert_triggered == True).all()

@router.get("/rooms")
async def list_ward_rooms(
    db: Session = Depends(get_db),
    nurse: User = Depends(get_nurse)
):
    from models import Room
    return db.query(Room).filter(Room.branch_id == nurse.branch_id).all()
