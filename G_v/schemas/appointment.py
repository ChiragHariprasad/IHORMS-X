"""
Appointment Schemas
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import date, time, datetime
from schemas.clinical import TelemetryResponse


class AppointmentBase(BaseModel):
    appointment_date: date
    appointment_time: time
    chief_complaint: Optional[str] = None


class AppointmentCreate(AppointmentBase):
    patient_id: int
    doctor_id: Optional[int] = None  # Optional - receptionist can assign


class AppointmentUpdate(BaseModel):
    appointment_date: Optional[date] = None
    appointment_time: Optional[time] = None
    doctor_id: Optional[int] = None
    room_id: Optional[int] = None
    chief_complaint: Optional[str] = None


class AppointmentReschedule(BaseModel):
    new_date: date
    new_time: time
    new_doctor_id: Optional[int] = None


class AppointmentResponse(BaseModel):
    id: int
    patient_id: int
    patient_name: str
    patient_uid: str
    doctor_id: int
    doctor_name: str
    specialization: str
    room_id: Optional[int]
    room_number: Optional[str]
    appointment_date: date
    appointment_time: time
    status: str
    chief_complaint: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class AppointmentDetailResponse(AppointmentResponse):
    notes: Optional[str]
    diagnosis: Optional[str]
    prescription: Optional[str]
    verdict: Optional[str]
    telemetry: List[TelemetryResponse] = []


class DoctorNotesUpdate(BaseModel):
    notes: str
    diagnosis: str
    prescription: str
    verdict: str


class AppointmentListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[AppointmentResponse]


class DoctorScheduleResponse(BaseModel):
    date: date
    appointments: List[AppointmentResponse]
    total_scheduled: int
    total_completed: int
    total_pending: int
