"""
Clinical Service - Handles telemetry and clinical operations
"""
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from decimal import Decimal

from models import (
    TelemetryData, Nurse, User, Equipment, Appointment, 
    Room, RoomType, Patient
)
from schemas.clinical import TelemetryCreate
from utils.exceptions import NotFoundError, ValidationError, ForbiddenError
from utils.audit import audit_logger


class ClinicalService:
    def __init__(self, db: Session):
        self.db = db
        
        # Vital thresholds for alerts
        self.thresholds = {
            'heart_rate': {'min': 60, 'max': 100},
            'blood_pressure_systolic': {'min': 90, 'max': 140},
            'blood_pressure_diastolic': {'min': 60, 'max': 90},
            'temperature': {'min': 97.0, 'max': 99.5},
            'oxygen_saturation': {'min': 95, 'max': 100},
            'respiratory_rate': {'min': 12, 'max': 20}
        }
    
    def check_vital_thresholds(self, data: TelemetryCreate) -> Tuple[bool, Optional[str]]:
        """Check if vitals are within normal range"""
        alerts = []
        
        if data.heart_rate:
            if data.heart_rate < self.thresholds['heart_rate']['min']:
                alerts.append(f"Low heart rate: {data.heart_rate} bpm")
            elif data.heart_rate > self.thresholds['heart_rate']['max']:
                alerts.append(f"High heart rate: {data.heart_rate} bpm")
        
        if data.blood_pressure_systolic:
            if data.blood_pressure_systolic < self.thresholds['blood_pressure_systolic']['min']:
                alerts.append(f"Low systolic BP: {data.blood_pressure_systolic}")
            elif data.blood_pressure_systolic > self.thresholds['blood_pressure_systolic']['max']:
                alerts.append(f"High systolic BP: {data.blood_pressure_systolic}")
        
        if data.oxygen_saturation:
            if data.oxygen_saturation < self.thresholds['oxygen_saturation']['min']:
                alerts.append(f"Low oxygen saturation: {data.oxygen_saturation}%")
        
        if data.temperature:
            temp = float(data.temperature)
            if temp < self.thresholds['temperature']['min']:
                alerts.append(f"Low temperature: {temp}F")
            elif temp > self.thresholds['temperature']['max']:
                alerts.append(f"High temperature: {temp}F")
        
        if alerts:
            return True, "; ".join(alerts)
        return False, None
    
    def add_telemetry(
        self, 
        data: TelemetryCreate, 
        nurse_user_id: int
    ) -> TelemetryData:
        """Nurse adds telemetry data for an appointment"""
        nurse = self.db.query(Nurse).filter(Nurse.user_id == nurse_user_id).first()
        if not nurse:
            raise NotFoundError("Nurse profile not found")
        
        appointment = self.db.query(Appointment).filter(
            Appointment.id == data.appointment_id
        ).first()
        if not appointment:
            raise NotFoundError("Appointment", str(data.appointment_id))
        
        # Check for alerts
        alert_triggered, alert_message = self.check_vital_thresholds(data)
        
        telemetry = TelemetryData(
            appointment_id=data.appointment_id,
            nurse_id=nurse.id,
            equipment_id=data.equipment_id,
            heart_rate=data.heart_rate,
            blood_pressure_systolic=data.blood_pressure_systolic,
            blood_pressure_diastolic=data.blood_pressure_diastolic,
            temperature=data.temperature,
            oxygen_saturation=data.oxygen_saturation,
            respiratory_rate=data.respiratory_rate,
            is_icu_patient=data.is_icu_patient,
            alert_triggered=alert_triggered,
            alert_message=alert_message,
            recorded_at=datetime.utcnow()
        )
        self.db.add(telemetry)
        
        audit_logger.log_action(
            self.db, nurse_user_id, "TELEMETRY_RECORDED", "TelemetryData", telemetry.id,
            after_state={"appointment_id": data.appointment_id, "alert": alert_triggered}
        )
        
        self.db.commit()
        return telemetry
    
    def get_telemetry_by_appointment(self, appointment_id: int) -> List[TelemetryData]:
        """Get all telemetry records for an appointment"""
        return self.db.query(TelemetryData).filter(
            TelemetryData.appointment_id == appointment_id
        ).order_by(TelemetryData.recorded_at.desc()).all()
    
    def get_equipment_by_branch(
        self, 
        branch_id: int, 
        operational_only: bool = False
    ) -> List[Equipment]:
        """Get equipment for a branch"""
        query = self.db.query(Equipment).filter(Equipment.branch_id == branch_id)
        if operational_only:
            query = query.filter(Equipment.is_operational == True)
        return query.all()
    
    def update_room_availability(self, room_id: int, is_available: bool, updated_by: int) -> Room:
        """Update room availability"""
        room = self.db.query(Room).filter(Room.id == room_id).first()
        if not room:
            raise NotFoundError("Room", str(room_id))
        
        room.is_available = is_available
        
        audit_logger.log_action(
            self.db, updated_by, "ROOM_AVAILABILITY_UPDATED", "Room", room_id,
            after_state={"is_available": is_available}
        )
        
        self.db.commit()
        return room
