"""
Clinical Schemas (Medical History, Telemetry)
"""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from decimal import Decimal


class MedicalHistoryResponse(BaseModel):
    id: int
    patient_id: int
    appointment_id: Optional[int]
    visit_date: datetime
    diagnosis: str
    symptoms: Optional[str]
    severity: Optional[str]
    treatment_given: Optional[str]
    medications: Optional[Dict[str, Any]]
    follow_up_required: bool
    follow_up_date: Optional[date]
    doctor_notes: Optional[str]
    lab_results: Optional[Dict[str, Any]]
    doctor_name: Optional[str]
    
    class Config:
        from_attributes = True


class MedicalHistoryListResponse(BaseModel):
    patient_id: int
    patient_name: str
    patient_uid: str
    total_records: int
    records: List[MedicalHistoryResponse]


class TelemetryCreate(BaseModel):
    appointment_id: int
    equipment_id: Optional[int] = None
    heart_rate: Optional[int] = None
    blood_pressure_systolic: Optional[int] = None
    blood_pressure_diastolic: Optional[int] = None
    temperature: Optional[Decimal] = None
    oxygen_saturation: Optional[int] = None
    respiratory_rate: Optional[int] = None
    is_icu_patient: bool = False


class TelemetryResponse(BaseModel):
    id: int
    appointment_id: int
    nurse_id: int
    nurse_name: str
    equipment_id: Optional[int]
    equipment_name: Optional[str]
    heart_rate: Optional[int]
    blood_pressure_systolic: Optional[int]
    blood_pressure_diastolic: Optional[int]
    temperature: Optional[Decimal]
    oxygen_saturation: Optional[int]
    respiratory_rate: Optional[int]
    is_icu_patient: bool
    alert_triggered: bool
    alert_message: Optional[str]
    recorded_at: datetime
    
    class Config:
        from_attributes = True


class RoomResponse(BaseModel):
    id: int
    branch_id: int
    room_number: str
    room_type: str
    floor: Optional[int]
    capacity: int
    capacity: int
    is_available: bool
    occupant_name: Optional[str] = None
    appointment_id: Optional[int] = None
    
    class Config:
        from_attributes = True


class EquipmentResponse(BaseModel):
    id: int
    branch_id: int
    name: str
    equipment_type: Optional[str]
    serial_number: str
    is_operational: bool
    last_maintenance: Optional[date]
    
    class Config:
        from_attributes = True


class AdmissionResponse(BaseModel):
    id: int
    patient_id: int
    patient_name: str
    doctor_id: int
    appointment_id: int
    room_id: Optional[int]
    room_number: Optional[str]
    room_type: Optional[str]
    admission_date: datetime
    status: str
    discharge_requested: bool
    
    class Config:
        from_attributes = True
